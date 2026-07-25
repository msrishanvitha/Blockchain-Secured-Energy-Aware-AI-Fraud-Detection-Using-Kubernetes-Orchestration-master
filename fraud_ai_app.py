from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the trained fraud detection pipeline
try:
    pipeline = joblib.load('fraud_model.pkl')
    print("Fraud detection model loaded successfully.")
except FileNotFoundError:
    print("ERROR: Model file 'fraud_model.pkl' not found.")
    print("Please run fraud_ai_train.py first to create the model.")
    pipeline = None

@app.route('/predict', methods=['POST'])
def predict_fraud():
    if pipeline is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        transaction = request.get_json()
        
        # 1. Convert the incoming JSON transaction into a DataFrame
        # The model pipeline expects the same features as training
        features_df = pd.DataFrame({
            'Amount': [transaction.get('Amount', 0)],
            'TimeOfDay': [transaction.get('TimeOfDay', 12.0)],
            'TransactionType': [transaction.get('TransactionType', 'ONLINE')]
        })

        # 2. Make prediction
        # model.predict() returns 1 for normal, -1 for fraud (anomaly)
        prediction = pipeline.predict(features_df)[0]
        
        # model.decision_function() gives the anomaly score
        score = pipeline.decision_function(features_df)[0]
        
        is_fraud = True if prediction == -1 else False

        # 3. Return the result
        return jsonify({
            "is_fraud": is_fraud,
            "anomaly_score": round(score, 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    print("\nStarting Fraud AI Flask server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
