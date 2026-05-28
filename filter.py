import socket
import ssl
import time
import requests
import base64
import statistics
import random

MAX_NODES = 80
TIMEOUT = 2.5

subs = open("subs.txt","r",encoding="utf-8").read().splitlines()

nodes = []

# -----------------------
# 1. LOAD SUBS
# -----------------------
for url in subs:
    try:
        r = requests.get(url, timeout=10)
        text = r.text.strip()

        try:
            decoded = base64.b64decode(text + "==").decode(errors="ignore")
        except:
            decoded = text

        for line in decoded.splitlines():
            if "vless://" in line or "vmess://" in line or "trojan://" in line:
                nodes.append(line)

    except:
        continue

nodes = nodes[:MAX_NODES]

print("TOTAL NODES:", len(nodes))


# -----------------------
# 2. PARSE
# -----------------------
parsed = []

for n in nodes:
    try:
        hp = n.split("@")[1]
        host = hp.split(":")[0]
        port = int(hp.split(":")[1].split("?")[0])
        parsed.append((host, port, n))
    except:
        continue


# -----------------------
# 3. MCI MOBILE SIMULATION MODEL
# -----------------------
def mci_mobile_model(lat):
    """
    Simulates real mobile network behavior:
    - jitter bursts
    - congestion spikes
    - unstable routing
    """

    jitter = random.uniform(0, lat * 0.4)
    spike = 0

    # occasional congestion spike (very important for MCI behavior)
    if random.random() < 0.2:
        spike = lat * random.uniform(0.5, 1.5)

    return lat + jitter + spike


# -----------------------
# 4. TEST NODE
# -----------------------
def test_node(host, port):
    samples = []

    for _ in range(3):
        try:
            start = time.time()

            sock = socket.create_connection((host, port), timeout=TIMEOUT)

            ctx = ssl.create_default_context()
            ssock = ctx.wrap_socket(sock, server_hostname=host)
            ssock.close()

            lat = time.time() - start

            # simulate MCI network behavior
            lat = mci_mobile_model(lat)

            samples.append(lat)

        except:
            return None

    avg = statistics.mean(samples)
    jitter = statistics.pstdev(samples)

    # MCI score model
    stability = 1 / (avg + jitter * 2)
    penalty = jitter * 1.8

    score = stability - penalty

    return avg, jitter, score


# -----------------------
# 5. RUN TESTS
# -----------------------
results = []

for i, (host, port, node) in enumerate(parsed):
    try:
        res = test_node(host, port)
        if res:
            avg, jitter, score = res
            results.append((score, avg, jitter, node))

        print(f"{i+1}/{len(parsed)}")

    except:
        continue


# -----------------------
# 6. SORT & CLASSIFY
# -----------------------
results.sort(reverse=True)

mci_best = [x[3] for x in results if x[0] > 2.8]
mci_stable = [x[3] for x in results if 1.3 < x[0] <= 2.8]
mci_weak = [x[3] for x in results if x[0] <= 1.3]


# -----------------------
# 7. OUTPUT
# -----------------------
open("mci_best.txt","w",encoding="utf-8").write("\n".join(mci_best))
open("mci_stable.txt","w",encoding="utf-8").write("\n".join(mci_stable))
open("mci_weak.txt","w",encoding="utf-8").write("\n".join(mci_weak))

print("MCI BEST:", len(mci_best))
print("MCI STABLE:", len(mci_stable))
print("MCI WEAK:", len(mci_weak))
print("DONE")
