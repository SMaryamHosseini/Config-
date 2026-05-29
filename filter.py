import requests
import base64
import re

SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

CDN = [
    "23.211", "2.16", "184.86", "104.66",
    "23.58", "172.225", "104.80",
    "23.210", "23.208", "23.42"
]

good = []

def decode_base64(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return ""

def extract_ip(line):
    m = re.search(r'@([\d\.]+):', line)
    return m.group(1) if m else None

for url in SUBS:
    print("FETCH:", url)

    raw = requests.get(url, timeout=20).text
    decoded = decode_base64(raw)

    lines = decoded.splitlines()

    print("LINES:", len(lines))

    for line in lines:
        if "vless://" not in line:
            continue

        ip = extract_ip(line)
        if not ip:
            continue

        for c in CDN:
            if ip.startswith(c):
                good.append(line)
                break

good = list(set(good))

with open("mci.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(good))

print("DONE")
print("GOOD:", len(good))
