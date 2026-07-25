from flask import Flask, request, jsonify
import hashlib, json, time, threading, requests, os

app = Flask(__name__)

chain = []
peers = set()
blockchain = []
LOCK = threading.Lock()

def hash_block(block):
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

def create_block(index, prev_hash, data):
    block = {
        "index": index,
        "prev_hash": prev_hash,
        "data": data,
        "ts": time.time(),
    }
    block["hash"] = hash_block(block)
    return block

# --- Blockchain Initialization ---
genesis_block = create_block(0, "0" * 64, {"genesis": True})
chain.append(genesis_block)

@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify({"connected": list(peers)})

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()
    peer = data.get("peer")
    if peer and peer not in peers:
        peers.add(peer)
        return jsonify({"ok": True, "peers": list(peers)})
    return jsonify({"ok": False, "reason": "invalid peer"}), 400

@app.route("/propose", methods=["POST"])
def propose_block():
    data = request.get_json()
    new_block = create_block(len(chain), chain[-1]["hash"], data)

    # PBFT-style quorum simulation
    quorum_needed = int(os.getenv("QUORUM", "2"))
    if len(peers) + 1 < quorum_needed:
        return jsonify({"ok": False, "reason": f"no quorum ({len(peers)+1}/3)"}), 409

    with LOCK:
        chain.append(new_block)
    return jsonify({"ok": True, "height": len(chain) - 1})

@app.route('/transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    if not data or "id" not in data or "amount" not in data or "account" not in data:
        return jsonify({"ok": False, "reason": "invalid transaction"}), 400

    # simple fraud detection: mark high value as fraudulent
    fraudulent = data["amount"] > 100000

    block = {
        "index": len(blockchain),
        "data": {
            **data,
            "fraudulent": fraudulent
        },
        "ts": time.time(),
        "hash": hashlib.sha256(json.dumps(data).encode()).hexdigest()
    }
    blockchain.append(block)
    return jsonify({"ok": True, "height": len(blockchain)-1}), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({"chain": blockchain, "height": len(blockchain)-1}), 200

# --- Auto Peer Discovery ---
def auto_join_peers():
    nodes = os.getenv("NODES", "").split(",")
    my_host = f"{os.getenv('HOSTNAME')}.blockchain.default.svc.cluster.local:7000"
    while True:
        for n in nodes:
            if n not in os.getenv("HOSTNAME", ""):
                try:
                    peer_url = f"http://{n}.blockchain.default.svc.cluster.local:7000/join"
                    requests.post(peer_url, json={"peer": my_host}, timeout=3)
                    peers.add(f"{n}.blockchain.default.svc.cluster.local:7000")
                except Exception:
                    pass
        time.sleep(10)

threading.Thread(target=auto_join_peers, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7000"))
    app.run(host="0.0.0.0", port=port)
