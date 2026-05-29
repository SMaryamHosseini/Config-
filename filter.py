import requests
import base64
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor

SUB_LINKS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

PORTS = [443, 80]

TIMEOUT = 1.2

mci_good = []
irancell_good = []
dead = []

def decode(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return text

def extract_ip(line):
    m = re.search(r'@([\d\.]+):', line)
    return m.group(1) if m else None

def tcp_test(ip, port):
    try:
        s = socket.socket()
        s.settimeout(TIMEOUT)

        start = time.time()
        s.connect((ip, port))
        latency = time.time() - start

        s.close()
        return True, latency
    except:
        return False, None

def classify(ip):
    ok_count = 0
    latency_sum = 0

    for p in PORTS:
        ok, lat = tcp_test(ip, p)
        if ok:
            ok_count += 1
            latency_sum += lat

    if ok_count == 2:
        avg = latency_sum / 2

        # heuristic ISP split
        if avg < 0.25:
            return "MCI"
        else:
            return "IRANCELL"

    elif ok_count == 1:
        return "MCI"

    return "DEAD"


def process(line):
    if "vless://" not in line:
        return None

    ip = extract_ip(line)
    if not ip:
        return None

    result = classify(ip)

    if result == "MCI":
        return ("MCI", line)

    if result == "IRANCELL":
        return ("IRANCELL", line)

    return None


for sub in SUB_LINKS:
    print("FETCH:", sub)

    raw = requests.get(sub, timeout=20).text
    decoded = decode(raw)

    lines = decoded.splitlines()
    print("TOTAL:", len(lines))

    results = []

    with ThreadPoolExecutor(max_workers=50) as ex:
        for r in ex.map(process, lines):
            if r:
                results.append(r)

    for t, v in results:
        if t == "MCI":
            mci_good.append(v)
        elif t == "IRANCELL":
            irancell_good.append(v)

mci_good = list(set(mci_good))
irancell_good = list(set(irancell_good))

print("MCI FOUND:", len(mci_good))
print("IRANCELL FOUND:", len(irancell_good))

with open("mci_best.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(mci_good))

with open("irancell.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(irancell_good))

with open("sub.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(mci_good + irancell_good))

print("DONE")
