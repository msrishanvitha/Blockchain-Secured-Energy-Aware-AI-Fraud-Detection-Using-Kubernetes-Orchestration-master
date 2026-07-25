from flask import Flask, request, jsonify
import requests, time, random, os

app = Flask(__name__)

BLOCKCHAIN_URL = os.getenv("BLOCKCHAIN_URL", "http://blockchain-0.blockchain.default.svc.cluster.local:7000")

# Simulated in-memory transaction queue
transactions = []

@app.route('/transaction', methods=['POST'])
def receive_transaction():
    """Receive a banking transaction"""
    tx = request.get_json()
    tx['timestamp'] = time.time()
    transactions.append(tx)

    # Simulate processing (fraud or not)
    result = classify_transaction(tx)

    # Log result to blockchain
    block = {
        "source": "transaction-service",
        "transaction_id": tx["id"],
        "amount": tx["amount"],
        "fraudulent": result,
        "processor_node": f"node-{random.randint(1, 3)}",
        "timestamp": tx["timestamp"]
    }
    try:
        r = requests.post(f"{BLOCKCHAIN_URL}/propose", json=block, timeout=5)
        print(f"[BLOCKCHAIN] Logged TX {tx['id']} → {r.status_code}")
    except Exception as e:
        print(f"[ERROR] Could not log TX {tx['id']}: {e}")

    return jsonify({"ok": True, "fraudulent": result})

def classify_transaction(tx):
    """Dummy fraud classifier — can later use ML model"""
    # simple rule or random choice
    return tx["amount"] > 50000 or random.random() < 0.1

@app.route('/transactions', methods=['GET'])
def list_transactions():
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7200)
