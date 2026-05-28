```python id="m2xph0"
import requests
import re

SUB_LINKS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

CDN_IPS = [
    "23.211",
    "2.16",
    "184.86",
    "104.66",
    "23.58",
    "172.225",
    "104.80",
    "23.210",
    "23.208",
    "23.42"
]

good = []

def extract_ip(cfg):
    try:
        m = re.search(r'@([\d\.]+):', cfg)
        if m:
            return m.group(1)
    except:
        pass
    return None

for sub in SUB_LINKS:

    try:
        text = requests.get(sub, timeout=20).text

        for line in text.splitlines():

            if not line.startswith("vless://"):
                continue

            ip = extract_ip(line)

            if not ip:
                continue

            for cdn in CDN_IPS:

                if ip.startswith(cdn):
                    good.append(line)
                    break

    except Exception as e:
        print("SUB ERROR:", e)

good = list(set(good))

with open("mci_best.txt", "w", encoding="utf-8") as f:
    for x in good:
        f.write(x + "\n")

with open("sub.txt", "w", encoding="utf-8") as f:
    for x in good:
        f.write(x + "\n")

print("FOUND:", len(good))
print("DONE")
```
