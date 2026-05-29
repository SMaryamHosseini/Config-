import requests
import socket
import re
import base64
import time

SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

TIMEOUT = 2

def decode(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return text

def extract_hosts(text):
    return re.findall(r'@([\w\.\-]+):', text)

def tcp_check(ip):
    try:
        s = socket.socket()
        s.settimeout(TIMEOUT)
        s.connect((ip, 443))
        s.close()
        return True
    except:
        return False

def latency(ip):
    try:
        start = time.time()
        s = socket.create_connection((ip, 443), timeout=TIMEOUT)
        s.close()
        return (time.time() - start) * 1000
    except:
        return 9999

results = []

for sub in SUBS:
    print("FETCH:", sub)

    raw = requests.get(sub, timeout=20).text
    decoded = decode(raw)

    hosts = list(set(extract_hosts(decoded)))

    print("TOTAL HOSTS:", len(hosts))

    for i, h in enumerate(hosts):
        if tcp_check(h):
            ping = latency(h)
            results.append((h, ping))

results = list(set(results))
results.sort(key=lambda x: x[1])

with open("result.txt", "w") as f:
    for ip, p in results:
        f.write(f"{ip} | {int(p)}ms\n")

print("DONE")
print("GOOD:", len(results))
