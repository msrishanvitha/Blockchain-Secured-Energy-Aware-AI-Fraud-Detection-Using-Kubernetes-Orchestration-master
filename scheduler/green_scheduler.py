from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from prometheus_client import start_http_server, Gauge
import requests, os, time, sys, random

print(" Green Scheduler started...")
sys.stdout.flush()

BLOCKCHAIN_URL = os.getenv("BLOCKCHAIN_URL",
    "http://blockchain-0.blockchain.default.svc.cluster.local:7000/propose")

# Prometheus metrics
carbon_intensity = Gauge("carbon_intensity", "Current carbon intensity (gCO2/kWh)")
renewable_percentage = Gauge("renewable_percentage", "Renewable share in electricity mix (%)")

# Start metrics endpoint
start_http_server(9100)
print(" Metrics server started on port 9100")

# Load Kubernetes config
try:
    config.load_incluster_config()
    print(" Using in-cluster config")
except ConfigException:
    config.load_kube_config()
    print(" Using local kube config")

apps_api = client.AppsV1Api()

def log_to_blockchain(ci, re, current, desired):
    """
    Logs each scaling decision as a blockchain transaction.
    """
    url = "http://blockchain-0.blockchain.default.svc.cluster.local:7000/propose"
    data = {
        "source": "green-scheduler",
        "carbon_intensity": ci,
        "renewable_percentage": re,
        "current_replicas": current,
        "desired_replicas": desired,
        "timestamp": time.time()
    }
    try:
        r = requests.post(url, json=data, timeout=5)
        if r.status_code == 200:
            print(f" Logged to blockchain successfully ✅")
        else:
            print(f" Blockchain log failed: HTTP {r.status_code}")
    except Exception as e:
        print(f" Blockchain log error: {e}")

def get_energy_data():
    token = os.getenv("ELECTRICITYMAP_TOKEN")
    url = "https://api.electricitymap.org/v3/carbon-intensity/latest?zone=IN"
    headers = {"auth-token": token}

    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            ci = data.get("carbonIntensity", 0)

            #  Simulate renewable percentage (since API gives 0 for India)
            re = data.get("renewablePercentage", 0)
            if re == 0:
                re = random.randint(40, 80)

            # Push metrics
            carbon_intensity.set(ci)
            renewable_percentage.set(re)
            print(f" CI={ci}, RE={re}")
            return ci, re

    except Exception as e:
        print(f" API Error: {e}")
    return None, None


while True:
    ci, re = get_energy_data()
    if ci is None:
        time.sleep(20)
        continue

    desired = 1
    if re >= 60 or ci < 400:
        desired = 2
    elif re >= 70 or ci < 300:
        desired = 3

    try:
        dep = apps_api.read_namespaced_deployment("web", "default")
        current = dep.spec.replicas
        if current != desired:
            dep.spec.replicas = desired
            apps_api.patch_namespaced_deployment("web", "default", dep)
            print(f" Scaled 'web' replicas {current} → {desired}")
            log_to_blockchain(ci, re, current, desired)
        else:
            print(f" No change (CI={ci}, RE={re}, replicas={current})")
        log_to_blockchain(ci, re, current, desired)
    except Exception as e:
        print(f" Scaling error: {e}")

    sys.stdout.flush()
    time.sleep(30)


