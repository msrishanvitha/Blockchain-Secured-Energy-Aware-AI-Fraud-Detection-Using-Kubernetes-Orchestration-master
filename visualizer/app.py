from flask import Flask, render_template, jsonify
import requests
import pandas as pd
import plotly.express as px
from io import StringIO

app = Flask(__name__)

# URL of your blockchain API (adjust namespace if different)
BLOCKCHAIN_URL = "http://blockchain-0.blockchain.default.svc.cluster.local:7000/chain"

def fetch_blockchain_data():
    try:
        data = requests.get(BLOCKCHAIN_URL).json()
        chain = data["chain"]
        blocks = []
        for b in chain:
            block_data = b["data"]
            block_data["index"] = b["index"]
            block_data["timestamp"] = b["ts"]
            blocks.append(block_data)
        return pd.DataFrame(blocks)
    except Exception as e:
        print("Error fetching blockchain:", e)
        return pd.DataFrame()

@app.route('/blocks')
def get_blocks():
    response = requests.get("http://blockchain-0.blockchain.default.svc.cluster.local:7000/chain")
    return jsonify(response.json())

@app.route('/transactions')
def get_transactions():
    response = requests.get("http://transaction-service.default.svc.cluster.local:7200/transactions")
    return jsonify(response.json())

@app.route("/")
def index():
    df = fetch_blockchain_data()
    if df.empty:
        return "<h3>No blockchain data found.</h3>"

    # Split by source
    scheduler_df = df[df["source"] == "green-scheduler"]
    tx_df = df[df["source"] == "transaction-service"]

    # Renewable Energy Trend
    fig1 = px.line(
        scheduler_df,
        x="timestamp",
        y="renewable_percentage",
        title="Renewable Energy % Over Time",
        markers=True
    )

    # Scaling Behavior
    fig2 = px.line(
        scheduler_df,
        x="timestamp",
        y=["current_replicas", "desired_replicas"],
        title="Replica Scaling Over Time"
    )

    # Transaction Results
    fig3 = px.scatter(
        tx_df,
        x="timestamp",
        y="amount",
        color="fraudulent",
        hover_data=["transaction_id", "processor_node"],
        title="Transaction Fraud Detection"
    )

    # Blockchain Growth
    fig4 = px.line(
        df,
        x="timestamp",
        y="index",
        title="Blockchain Growth (Block Height Over Time)"
    )

    html = f"""
    <html>
      <head><title>Blockchain Visualizer</title></head>
      <body>
        <h1>🌐 Blockchain & Transaction Visualizer</h1>
        {fig1.to_html(full_html=False, include_plotlyjs='cdn')}
        {fig2.to_html(full_html=False, include_plotlyjs='cdn')}
        {fig3.to_html(full_html=False, include_plotlyjs='cdn')}
        {fig4.to_html(full_html=False, include_plotlyjs='cdn')}
      </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
