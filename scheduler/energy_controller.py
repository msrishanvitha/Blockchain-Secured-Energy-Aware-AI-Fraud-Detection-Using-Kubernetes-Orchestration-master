from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from prometheus_client import start_http_server, Gauge
import requests
import time
import sys
import os

print(" Starting Energy Controller...")
sys.stdout.flush()

# --- Prometheus Metrics ---
green_score_gauge = Gauge("green_score", "Current green score value from green-ai service")
replica_gauge = Gauge("web_replicas", "Number of web replicas in deployment")

# Start metrics server early
METRICS_PORT = int(os.getenv("METRICS_PORT", "9101"))
start_http_server(METRICS_PORT)
print(f" Prometheus metrics endpoint running on port {METRICS_PORT}")
sys.stdout.flush()

# --- Kubernetes Configuration ---
try:
    config.load_incluster_config()
    print(" Loaded in-cluster config")
except ConfigException:
    config.load_kube_config()
    print(" Loaded local kubeconfig")
except Exception as e:
    print(f" Could not load Kubernetes config: {e}")
    sys.exit(1)

# --- Kubernetes API Client ---
try:
    apps_api = client.AppsV1Api()
    print(" Kubernetes AppsV1 API client initialized")
except Exception as e:
    print(f" Failed to create Kubernetes API client: {e}")
    sys.exit(1)

# --- Helper Function ---
def get_green_score():
    """Fetch current green score from green-ai service"""
    url = "http://green-ai-service.default.svc.cluster.local:8000/v1/energy/now"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            score = float(data.get("green_score", 0.0))
            print(f" Fetched green score: {score:.2f}")
            return score
        else:
            print(f" HTTP {resp.status_code} from {url}")
            return 0.0
    except requests.exceptions.RequestException as e:
        print(f" Request error: {e}")
        return 0.0
    except Exception as e:
        print(f" Unexpected error fetching score: {e}")
        return 0.0

# --- Main Control Loop ---
print(" Energy Controller is now monitoring energy data...")
sys.stdout.flush()

while True:
    try:
        # Step 1: Fetch the current green energy score
        score = get_green_score()
        green_score_gauge.set(score)

        # Step 2: Read current deployment details
        dep = apps_api.read_namespaced_deployment("web", "default")
        current_replicas = dep.spec.replicas
        replica_gauge.set(current_replicas)

        # Step 3: Decide scaling rule
        min_threshold = 0.6
        desired_replicas = 2 if score >= min_threshold else 1

        # Step 4: Apply scaling if needed
        if desired_replicas != current_replicas:
            print(f" Score {score:.2f} — scaling 'web' replicas {current_replicas} ➜ {desired_replicas}")
            dep.spec.replicas = desired_replicas
            apps_api.patch_namespaced_deployment("web", "default", dep)
            print(f" Scaled 'web' deployment to {desired_replicas} replicas")
        else:
            print(f" Score {score:.2f} — keeping 'web' replicas at {current_replicas}")

        sys.stdout.flush()
        time.sleep(15)

    except Exception as e:
        print(f" Controller loop error: {e}")
        sys.stdout.flush()
        time.sleep(10)
