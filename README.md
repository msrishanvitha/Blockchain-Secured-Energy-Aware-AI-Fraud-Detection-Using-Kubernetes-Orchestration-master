# Blockchain-Secured Energy-Aware AI Fraud Detection Using Kubernetes Orchestration

A microservices system that combines **AI-based fraud detection**, **energy/carbon-aware scheduling**, and **blockchain-backed audit logging**, all orchestrated on **Kubernetes**. The goal is to detect fraudulent transactions while scheduling compute workloads to run when and where renewable energy availability is highest, and to record every decision immutably on-chain for auditability.

## Architecture Overview

The system is composed of independent services, each containerized and deployed via Kubernetes manifests in `infrastructure/k8s/`:

| Service | Description |
|---|---|
| **fraud_ai** | Flask service serving an Isolation Forest model that scores incoming transactions as fraudulent or normal, exposing Prometheus metrics. |
| **green_ai** | FastAPI service that reports current carbon intensity, renewable energy share, and a normalized "green score" for a given region/time. |
| **scheduler / green_scheduler** | Watches the green score and cluster state, and scales/schedules Kubernetes workloads (via the Kubernetes API) toward times/regions with cleaner energy. |
| **collector** | Periodically pulls regional renewable-energy percentages (e.g. from ElectricityMap/OpenWeatherMap-style sources) and exposes them as Prometheus gauges. |
| **blockchain (green-fraud-blockchain)** | Node.js/Solidity service (`AuditLog.sol` / `FraudLog.sol`) that logs each fraud decision — transaction ID, region, fraud flag, AI confidence, and carbon intensity — immutably on a blockchain ledger via Web3. |
| **visualizer** | Flask + Plotly dashboard for visualizing fraud detections, green scores, and energy data over time. |

Regional training data (`france_data.csv`, `germany_data.csv`, `spain_data.csv`) and per-region trained models (`node_a_germany_model.pkl`, `node_b_france_model.pkl`, `node_c_spain_model.pkl`) support a federated-style setup across simulated regions.

Monitoring is handled via Prometheus and Grafana (see `infrastructure/monitoring/` and the Grafana/Prometheus manifests in `infrastructure/k8s/`).

## Repository Structure

```
.
├── fraud_ai/                # Fraud detection service (Flask)
├── green_ai/                # Green/carbon scoring service (FastAPI)
├── scheduler/                # Kubernetes-aware green scheduler + blockchain/transaction services
├── collector/                # Regional renewable-energy data collector
├── visualizer/               # Dashboard for fraud + energy data
├── blockchain/
│   └── green-fraud-blockchain/  # Node.js/Solidity smart contract + Web3 server
├── contracts/                # Solidity smart contracts (AuditLog.sol)
├── infrastructure/
│   ├── k8s/                  # Kubernetes manifests for all services
│   └── monitoring/           # Prometheus/Grafana manifests
├── shared/                   # Shared schemas (e.g. fraud_log_schema.json)
├── fraud_ai_train.py         # Trains the fraud detection model
├── green_ai_train.py         # Trains the green/carbon forecasting model
├── *_data.csv                # Regional training datasets
├── *_model.pkl               # Pre-trained models
└── requirements.txt          # Consolidated Python dependencies
```

## Prerequisites

- Python 3.9+
- Node.js 18+ (for the blockchain service)
- Docker
- A running Kubernetes cluster (e.g. Minikube) with `kubectl` configured
- (Optional) Prometheus + Grafana for monitoring

## Setup

### 1. Clone and install Python dependencies
```bash
git clone <your-repo-url>
cd Blockchain-Secured-Energy-Aware-AI-Fraud-Detection-Using-Kubernetes-Orchestration-master
pip install -r requirements.txt
```

Each service also has its own `requirements.txt` if you prefer isolated virtual environments per service (e.g. `fraud_ai/requirements.txt`).

### 2. Install blockchain service dependencies
```bash
cd blockchain/green-fraud-blockchain
npm install
```

### 3. Train the models (optional — pre-trained `.pkl` files are included)
```bash
python fraud_ai_train.py
python green_ai_train.py
```

### 4. Build and deploy services to Kubernetes
Each service has its own `Dockerfile`. Build and push images, then apply the manifests:
```bash
docker build -t <your-registry>/fraud_ai ./fraud_ai
docker build -t <your-registry>/green_ai ./green_ai
docker build -t <your-registry>/scheduler ./scheduler
docker build -t <your-registry>/collector ./collector
docker build -t <your-registry>/visualizer ./visualizer

kubectl apply -f infrastructure/k8s/
```

### 5. CI/CD
A GitHub Actions workflow (`.github/workflows/build.yml`) builds, scans (Trivy), and signs (Cosign) each service image on push/PR to `main`. If you want image signing to work, add a `COSIGN_KEY` secret to your repo rather than committing any key.

## Notes

- Do not commit `node_modules/` — see `.gitignore`. Run `npm install` inside `blockchain/green-fraud-blockchain/` after cloning.
- No API keys or secrets are included in this repo; set any required keys (e.g. `ELECTRICITYMAP_KEY`, `OPENWEATHERMAP_KEY`) as environment variables or Kubernetes secrets.

## License

Smart contracts are marked MIT-licensed (`AuditLog.sol`). Add a `LICENSE` file at the repo root if you want the whole project covered by a specific license.
