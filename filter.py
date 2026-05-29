import requests
import base64
import re

SUBS = [
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"
]

# فقط این مدل‌ها رو نگه میداریم:
# ws + no tls + port 80/8080

good = []

# ---------- decode ----------
def decode_sub(text):
    try:
        return base64.b64decode(text).decode("utf-8", errors="ignore")
    except:
        return text

# ---------- extract ----------
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

        # بدون tls/reality
        if "security=tls" in lower:
            continue

        if "security=reality" in lower:
            continue

        # فقط 80/8080
        m = re.search(r'@[^:]+:(\d+)', line)

        if not m:
            continue

        port = m.group(1)

        if port not in ["80", "8080"]:
            continue

        # استخراج host
        host_match = re.search(r'host=([^&]+)', line)

        host = host_match.group(1) if host_match else ""

        # دامنه‌های مشکوک CDN حذف
        bad_words = [
            "cloudflare",
            "akamai",
            "cdn",
            "edge",
            "fastly"
        ]

        bad = False

        for b in bad_words:
            if b in host.lower():
                bad = True
                break

        if bad:
            continue

        good.append(line)

# حذف تکراری
good = list(set(good))

# ذخیره
with open("mci.txt", "w", encoding="utf-8") as f:
    for x in good:
        f.write(x + "\n")

print("DONE")
print("GOOD:", len(good))
