import requests
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

def extract_ip(line):
    m = re.search(r'@([\d\.]+):', line)
    return m.group(1) if m else None

for url in SUBS:
    print("FETCH:", url)
    text = requests.get(url, timeout=20).text

    for line in text.splitlines():
        if not line.startswith("vless://"):
            continue

        ip = extract_ip(line)
        if not ip:
            continue

        for c in CDN:
            if ip.startswith(c):
                good.append(line)   # ✔️ مهم: کل کانفیگ
                break

good = list(set(good))

with open("mci.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(good))

with open("irancell.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(good))

print("DONE")
print("GOOD:", len(good))
