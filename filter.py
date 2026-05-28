import socket
import ssl
import time
import requests
import base64
import statistics

MAX_NODES = 80
TIMEOUT = 2

subs = open("subs.txt","r",encoding="utf-8").read().splitlines()

nodes = []

# -----------------------
# 1. extract nodes
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
# 3. MULTI METRIC TEST
# -----------------------
def test_node(host, port):
    latencies = []

    for _ in range(3):  # multi-sample (important)
        try:
            start = time.time()

            sock = socket.create_connection((host, port), timeout=TIMEOUT)

            # TLS handshake test (realistic quality check)
            ctx = ssl.create_default_context()
            ssock = ctx.wrap_socket(sock, server_hostname=host)

            ssock.close()

            latencies.append(time.time() - start)

        except:
            return None

    if not latencies:
        return None

    avg = statistics.mean(latencies)
    jitter = statistics.pstdev(latencies) if len(latencies) > 1 else 0

    # scoring model (MCI-like weighting)
    score = (1 / avg) - (jitter * 2)

    return avg, jitter, score


# -----------------------
# 4. RUN TESTS
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
# 5. SORTING (REAL QUALITY)
# -----------------------
results.sort(reverse=True)

best = [x[3] for x in results if x[0] > 5]
stable = [x[3] for x in results if 2 < x[0] <= 5]
weak = [x[3] for x in results if x[0] <= 2]


# -----------------------
# 6. OUTPUT FILES
# -----------------------
open("mci_best.txt","w",encoding="utf-8").write("\n".join(best))
open("mci_stable.txt","w",encoding="utf-8").write("\n".join(stable))
open("mci_weak.txt","w",encoding="utf-8").write("\n".join(weak))

print("BEST:", len(best))
print("STABLE:", len(stable))
print("WEAK:", len(weak))
print("DONE")
