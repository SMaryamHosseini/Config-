import requests
import base64
import re
import socket
import ssl
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor

SUB_LINKS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

TIMEOUT = 1.2
SNI = "www.google.com"

ASN_API = "https://ipinfo.io/"

mci = []
irancell = []
unstable = []

def decode(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return text

def extract_ip(line):
    m = re.search(r'@([\d\.]+):', line)
    return m.group(1) if m else None


# 🌐 REAL ASN CHECK
def get_asn(ip):
    try:
        r = requests.get(f"{ASN_API}{ip}/json", timeout=2)
        data = r.json()
        return data.get("org", "UNKNOWN")
    except:
        return "UNKNOWN"


# 🌐 TRACEROUTE CHECK (light version)
def trace(ip):
    try:
        result = subprocess.run(
            ["traceroute", "-m", "10", ip],
            capture_output=True,
            text=True,
            timeout=3
        )
        return result.stdout
    except:
        return ""


# 🔐 TLS TEST
def tls_test(ip):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        s = socket.create_connection((ip, 443), timeout=TIMEOUT)
        s.settimeout(TIMEOUT)

        start = time.time()
        ssl_sock = context.wrap_socket(s, server_hostname=SNI)
        ssl_sock.close()

        return True, time.time() - start
    except:
        return False, None


def score(ip):
    asn = get_asn(ip)
    trace_data = trace(ip)
    ok, lat = tls_test(ip)

    if not ok:
        return "BAD"

    s = 0

    # ASN scoring
    if "MCI" in asn or "Telecommunication" in asn:
        s += 4

    if "Cloudflare" in asn:
        s -= 3

    # latency scoring
    if lat < 0.2:
        s += 3
    elif lat < 0.5:
        s += 1

    # traceroute heuristic
    if "10." in trace_data or "192.168" in trace_data:
        s += 2

    if s >= 5:
        return "MCI"
    elif s >= 2:
        return "IRANCELL"
    else:
        return "UNSTABLE"


def process(line):
    if "vless://" not in line:
        return None

    ip = extract_ip(line)
    if not ip:
        return None

    result = score(ip)

    if result == "MCI":
        return ("MCI", line)
    elif result == "IRANCELL":
        return ("IRANCELL", line)
    else:
        return ("UNSTABLE", line)


for sub in SUB_LINKS:
    print("FETCH:", sub)

    raw = requests.get(sub, timeout=20).text
    decoded = decode(raw)

    lines = decoded.splitlines()
    print("TOTAL:", len(lines))

    results = []

    with ThreadPoolExecutor(max_workers=30) as ex:
        for r in ex.map(process, lines):
            if r:
                results.append(r)

for t, v in results:
    if t == "MCI":
        mci.append(v)
    elif t == "IRANCELL":
        irancell.append(v)
    else:
        unstable.append(v)

mci = list(set(mci))
irancell = list(set(irancell))
unstable = list(set(unstable))

print("MCI:", len(mci))
print("IRANCELL:", len(irancell))
print("UNSTABLE:", len(unstable))

with open("mci_best.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(mci))

with open("irancell.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(irancell))

with open("sub.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(mci + irancell))

print("DONE")
