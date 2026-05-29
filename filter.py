import requests
import base64
import re
from urllib.parse import unquote

SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

domains = []

# ---------- decode ----------
def decode_sub(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return text

# ---------- extract host ----------
def extract_host(cfg):

    # host=
    m = re.search(r'host=([^&]+)', cfg, re.IGNORECASE)

    if m:
        return unquote(m.group(1)).strip()

    # sni=
    m = re.search(r'sni=([^&]+)', cfg, re.IGNORECASE)

    if m:
        return unquote(m.group(1)).strip()

    return None

# ---------- process ----------
for sub in SUBS:

    print("FETCH:", sub)

    try:
        raw = requests.get(sub, timeout=20).text
        decoded = decode_sub(raw)

    except Exception as e:
        print("SUB ERROR:", e)
        continue

    lines = decoded.splitlines()

    print("LINES:", len(lines))

    for line in lines:

        line = line.strip()

        # فقط vless
        if not line.startswith("vless://"):
            continue

        lower = line.lower()

        # فقط ws
        if "type=ws" not in lower:
            continue

        # فقط بدون tls/reality
        if "security=tls" in lower:
            continue

        if "security=reality" in lower:
            continue

        # فقط پورت 80/8080
        m = re.search(r'@[^:]+:(\d+)', line)

        if not m:
            continue

        port = m.group(1)

        if port not in ["80", "8080"]:
            continue

        host = extract_host(line)

        if not host:
            continue

        # حذف CDN معروف
        bad_words = [
            "cloudflare",
            "akamai",
            "fastly",
            "cdn",
            "edge",
            "workers"
        ]

        skip = False

        for b in bad_words:
            if b in host.lower():
                skip = True
                break

        if skip:
            continue

        domains.append(host)

# unique
domains = sorted(list(set(domains)))

# save
with open("mci_domains.txt", "w", encoding="utf-8") as f:

    for d in domains:
        f.write(d + "\n")

print("DONE")
print("DOMAINS:", len(domains))
