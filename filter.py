import base64
import json
import urllib.request
from urllib.parse import urlparse

SOURCE = "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_base64_Sub.txt"

NETWORKS = {
    "Asia": [
        "185.",
        "104.",
        "23.",
        "34.",
    ],

    "MCI": [
        "104.",
        "188.",
    ],

    "Samantel": [
        "2.",
        "23.",
        "34.",
        "92.",
        "104.",
        "141.",
        "162.",
        "167.",
        "172.",
        "185.",
        "190.",
        "199.",
    ],

    "Mobinnet": [
        "2.",
        "23.",
        "34.",
        "104.",
        "151.",
        "167.",
        "172.",
        "184.",
        "199.",
    ],
}


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


def clean_host(host):
    if not host:
        return None
    return host.split(":")[0].strip()


# download + decode
raw = urllib.request.urlopen(SOURCE, timeout=30).read().decode()

decoded = base64.b64decode(raw).decode("utf-8", errors="ignore")

results = {name: [] for name in NETWORKS}

for line in decoded.splitlines():

    line = line.strip()
    if not line:
        continue

    host = clean_host(get_host(line))

    if not host:
        continue

    for name, prefixes in NETWORKS.items():
        if host.startswith(tuple(prefixes)):
            results[name].append((host, line))  # store host + config


# write outputs
for name, items in results.items():

    # dedupe by HOST (روش 2)
    unique = {}
    for host, cfg in items:
        if host not in unique:
            unique[host] = cfg

    unique_configs = list(unique.values())

    encoded = base64.b64encode(
        "\n".join(unique_configs).encode()
    ).decode()

    with open(f"{name}.txt", "w", encoding="utf-8") as f:
        f.write(encoded)

    print(f"{name}: {len(items)} -> {len(unique_configs)}")
