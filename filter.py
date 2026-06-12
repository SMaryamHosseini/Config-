import base64
import json
import urllib.request
from urllib.parse import urlparse

SOURCE = "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"

NETWORKS = {
    "Asia": ["185.", "104.", "23.", "34."],

    "MCI": ["104.", "188."],

    "Samantel": [
        "2.", "23.", "34.", "104.","141","167","172","185","190.","199"
    ],

    "Mobinnet": [
        "2.", "23.", "34.", "104.", "151.", "167.",
        "172.", "184.", "199."
    ],
}


# ----------------------------
# Extract host from configs
# ----------------------------
def get_host(line):
    try:
        # VLESS / TROJAN
        if line.startswith(("vless://", "trojan://")):
            return urlparse(line).hostname

        # VMESS
        if line.startswith("vmess://"):
            raw = line[8:]
            raw += "=" * (-len(raw) % 4)

            data = json.loads(
                base64.b64decode(raw).decode("utf-8", errors="ignore")
            )

            return data.get("add")

    except:
        return None

    return None


# ----------------------------
# Clean host (remove port)
# ----------------------------
def clean_host(host):
    if not host:
        return None
    return host.split(":")[0].strip()


# ----------------------------
# Download + decode source
# ----------------------------
raw = urllib.request.urlopen(SOURCE, timeout=30).read().decode()

decoded = base64.b64decode(raw).decode("utf-8", errors="ignore")


# ----------------------------
# Store results (dedupe by host)
# ----------------------------
results = {name: {} for name in NETWORKS}


for line in decoded.splitlines():

    line = line.strip()
    if not line:
        continue

    host = clean_host(get_host(line))

    if not host:
        continue

    for name, prefixes in NETWORKS.items():

        if host.startswith(tuple(prefixes)):

            # dedupe by host (final fix)
            results[name][host] = line


# ----------------------------
# Write output files
# ----------------------------
for name, items in results.items():

    unique_configs = list(items.values())

    encoded = base64.b64encode(
        "\n".join(unique_configs).encode()
    ).decode()

    with open(f"{name}.txt", "w", encoding="utf-8") as f:
        f.write(encoded)

    print(f"{name}: {len(unique_configs)}")
