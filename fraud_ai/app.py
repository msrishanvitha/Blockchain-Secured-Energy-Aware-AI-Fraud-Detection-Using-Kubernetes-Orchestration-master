# fraud_ai/app.py
from flask import Flask, request, jsonify, Response
import joblib
import pandas as pd
import os
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Load model if present
MODEL_PATH = os.getenv('MODEL_PATH', 'fraud_model.pkl')
try:
    pipeline = joblib.load(MODEL_PATH)
    print("Fraud model loaded")
except Exception as e:
    print("Fraud model not loaded:", e)
    pipeline = None

# Prometheus metric
fraud_detected_gauge = Gauge('fraud_detected_total', 'Number of frauds detected', ['node'])
request_count = Gauge('fraud_requests_total', 'Total fraud requests', ['node'])

NODE_NAME = os.getenv('NODE_NAME', 'node-unknown')

@app.route('/predict', methods=['POST'])
def predict_fraud():
    request_count.labels(node=NODE_NAME).inc()
    if pipeline is None:
        return jsonify({"error":"Model not loaded"}), 500
    try:
        txn = request.get_json()
        features_df = pd.DataFrame({
            'Amount': [txn.get('Amount',0)],
            'TimeOfDay': [txn.get('TimeOfDay',12.0)],
            'TransactionType': [txn.get('TransactionType','ONLINE')]
        })
        pred = pipeline.predict(features_df)[0]
        score = pipeline.decision_function(features_df)[0]
        is_fraud = True if pred == -1 else False
        if is_fraud:
            fraud_detected_gauge.labels(node=NODE_NAME).inc()
        return jsonify({"is_fraud": is_fraud, "anomaly_score": round(float(score),4)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
