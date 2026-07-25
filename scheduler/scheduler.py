from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from prometheus_client import start_http_server, Gauge
import requests
import time
import sys

print("--- Scheduler script started ---")
sys.stdout.flush()

# --- Prometheus Metrics ---
green_score_gauge = Gauge("green_score", "Current green score value")
replica_gauge = Gauge("web_replicas", "Number of web replicas")

# Start metrics server BEFORE scheduler loop
start_http_server(9100)
print(" Prometheus metrics endpoint started on port 9100")
sys.stdout.flush()

# --- Load Kubernetes Configuration ---
try:
    config.load_incluster_config()
    print(" Loaded in-cluster Kubernetes config")
except ConfigException:
    config.load_kube_config()
    print(" Loaded local kubeconfig")
except Exception as e:
    print(f" FAILED to load kube config: {e}")
    sys.exit(1)

# --- Create Kubernetes Clients ---
try:
    apps_api = client.AppsV1Api()
    print(" Kubernetes AppsV1 client ready.")
except Exception as e:
    print(f" FAILED to create API client: {e}")
    sys.exit(1)

# --- Helper Function ---
def get_green_score():
    """Fetch green energy metrics from green-ai service"""
    try:
        resp = requests.get("http://green-ai-service.default.svc.cluster.local:8000/v1/energy/now", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return float(data["green_score"])
        else:
            print(f" HTTP {resp.status_code} from green-ai-service")
            return 0.0
    except Exception as e:
        print(f" Error fetching green score: {e}")
        return 0.0

# --- Scheduler Logic ---
print(" Scheduler running. Entering main control loop...")
sys.stdout.flush()

while True:
    try:
        score = get_green_score()
        print(f"Current green_score = {score:.2f}")
        sys.stdout.flush()
        green_score_gauge.set(score)

        # Get current deployment
        dep = apps_api.read_namespaced_deployment("web", "default")
        current_replicas = dep.spec.replicas
        replica_gauge.set(current_replicas)

        # Define scaling rule
        min_green_threshold = 0.6
        desired_replicas = 2 if score >= min_green_threshold else 1

        # Apply scaling
        if desired_replicas != current_replicas:
            dep.spec.replicas = desired_replicas
            apps_api.patch_namespaced_deployment("web", "default", dep)
            print(f" Adjusted web replicas → {desired_replicas}")
            sys.stdout.flush()

        time.sleep(15)

    except Exception as e:
        print(f" Scheduler loop error: {e}")
        sys.stdout.flush()
        time.sleep(10)
