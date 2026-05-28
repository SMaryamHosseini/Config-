import requests
import socket
import ssl
import base64

# -----------------------
# CONFIG (خیلی مهم)
# -----------------------
MAX_NODES = 50
SOCKET_TIMEOUT = 2

socket.setdefaulttimeout(SOCKET_TIMEOUT)

subs = open("subs.txt","r",encoding="utf-8").read().splitlines()

nodes = []

# -----------------------
# 1. extract nodes
# -----------------------
for url in subs:
    try:
        r = requests.get(url, timeout=10)
        text = r.text.strip()

        # try base64 decode
        try:
            decoded = base64.b64decode(text + "==").decode(errors="ignore")
        except:
            decoded = text

        for line in decoded.splitlines():
            line = line.strip()
            if "vless://" in line or "vmess://" in line or "trojan://" in line:
                nodes.append(line)

    except:
        continue

# limit to prevent freeze
nodes = nodes[:MAX_NODES]

print("TOTAL NODES:", len(nodes))


# -----------------------
# 2. SAFE TLS CHECK
# -----------------------
def test_node(host, port):
    try:
        ctx = ssl.create_default_context()
        sock = socket.create_connection((host, port), timeout=2)
        ssock = ctx.wrap_socket(sock, server_hostname=host)
        ssock.close()
        return True
    except:
        return False


# -----------------------
# 3. test loop (SAFE)
# -----------------------
good = []

for i, n in enumerate(nodes):
    try:
        if "@" not in n:
            continue

        hp = n.split("@")[1]
        host = hp.split(":")[0]
        port = int(hp.split(":")[1].split("?")[0])

        if test_node(host, port):
            good.append(n)

        print(f"{i+1}/{len(nodes)} checked")

    except:
        continue


# -----------------------
# 4. OUTPUT (always create file)
# -----------------------
with open("mci_best.txt","w",encoding="utf-8") as f:
    f.write("\n".join(good))

print("GOOD NODES:", len(good))
print("DONE")
