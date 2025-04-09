from fastapi import FastAPI
from pydantic import BaseModel
import psutil
import time
import threading
import ping3
import socket
import os

app = FastAPI()

# ------------------- Config --------------------
NODE_NAME = socket.gethostname()

# PING3 fix
ping3.EXCEPTIONS = True
ping3.udp = True

def load_peer_nodes(filepath="peers.txt") -> list[str]:
    try:
        with open(filepath, "r") as f:
            peers = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return peers
    except Exception as e:
        print(f"[WARN] Failed to read {filepath}: {e}")
        return []

# ------------------- Globals --------------------
cpu_usage = 0.0
mem_usage = 0.0
net_rx_mbps = 0.0
net_tx_mbps = 0.0
latency_map = {}

net_last = psutil.net_io_counters()
net_last_time = time.time()
net_lock = threading.Lock()

# ------------------- Sampling Threads --------------------

def sample_cpu():
    global cpu_usage
    psutil.cpu_percent(interval=None)
    while True:
        cpu_usage = psutil.cpu_percent(interval=1) / 100


def sample_mem():
    global mem_usage
    while True:
        mem = psutil.virtual_memory()
        mem_usage = mem.used / mem.total
        time.sleep(1)


def sample_net():
    global net_last, net_last_time, net_rx_mbps, net_tx_mbps
    while True:
        with net_lock:
            curr = psutil.net_io_counters()
            now = time.time()
            rx_rate = (curr.bytes_recv - net_last.bytes_recv) * 8 / (now - net_last_time) / 1e6
            tx_rate = (curr.bytes_sent - net_last.bytes_sent) * 8 / (now - net_last_time) / 1e6
            net_rx_mbps = round(rx_rate, 2)
            net_tx_mbps = round(tx_rate, 2)
            net_last = curr
            net_last_time = now
        time.sleep(1)


# def sample_latency():
#     global latency_map
#     while True:
#         peer_nodes = load_peer_nodes()
#         results = {}
#         for peer in peer_nodes:
#             try:
#                 delay = ping3.ping(peer, timeout=1)
#                 results[peer] = round(delay * 1000, 2) if delay else None
#             except Exception:
#                 results[peer] = None
#         latency_map = results
#         time.sleep(5)

def sample_latency():
    global latency_map
    while True:
        peer_nodes = load_peer_nodes()
        results = {}
        for peer in peer_nodes:
            try:
                delay = ping3.ping(peer, timeout=1)
                print(f"[DEBUG] Ping {peer} = {delay}")
                results[peer] = round(delay * 1000, 2) if delay else None
            except Exception as e:
                print(f"[ERROR] Ping {peer} failed: {e}")
                results[peer] = None
        latency_map = results
        time.sleep(5)


# ------------------- FastAPI Endpoint --------------------
class NetStat(BaseModel):
    rx: float
    tx: float


class StatResponse(BaseModel):
    nodeName: str
    timestamp: int
    cpu: float
    mem: float
    net: NetStat
    latency: dict


@app.get("/stats", response_model=StatResponse)
def get_stats():
    return StatResponse(
        nodeName=NODE_NAME,
        timestamp=int(time.time()),
        cpu=round(cpu_usage, 4),
        mem=round(mem_usage, 4),
        net=NetStat(rx=net_rx_mbps, tx=net_tx_mbps),
        latency=latency_map
    )


# ------------------- Start Threads --------------------
threading.Thread(target=sample_cpu, daemon=True).start()
threading.Thread(target=sample_mem, daemon=True).start()
threading.Thread(target=sample_net, daemon=True).start()
threading.Thread(target=sample_latency, daemon=True).start()
