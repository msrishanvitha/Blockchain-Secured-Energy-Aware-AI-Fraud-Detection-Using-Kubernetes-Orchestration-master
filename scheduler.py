from kubernetes import client, config
import requests, time

# Load kubeconfig from local environment (works inside minikube or from host)
config.load_kube_config()
apps_api = client.AppsV1Api()
custom_api = client.CustomObjectsApi()

# --- Helper Functions ---
def get_green_score():
    """Fetch latest green energy score from the green_ai service"""
    try:
        resp = requests.get("http://green-ai-service.default.svc.cluster.local:8000/v1/energy/now", timeout=5)
        return resp.json()["green_score"]
    except Exception as e:
        print("Error fetching green score:", e)
        return 0.0

def get_policy():
    """Fetch energy policy from CRD"""
    try:
        policy = custom_api.get_namespaced_custom_object(
            group="scheduling.greenai.dev",
            version="v1",
            namespace="default",
            plural="energypolicies",
            name="default-policy"
        )
        return policy["spec"]["minGreenScore"], policy["spec"]["splitThreshold"]
    except Exception as e:
        print("Error fetching policy:", e)
        return 0.6, 0.1  # default fallback

# --- Main Loop ---
while True:
    score = get_green_score()
    min_green, _ = get_policy()

    print(f"\nCurrent green_score = {score:.2f} | Policy threshold = {min_green}")
    dep = apps_api.read_namespaced_deployment("web", "default")

    if score >= min_green:
        # scale up to 2 replicas when green
        if dep.spec.replicas < 2:
            dep.spec.replicas = 2
            apps_api.patch_namespaced_deployment("web", "default", dep)
            print("🌱 Green condition met — scaled UP web deployment.")
    else:
        # scale down to 1 replica when not green
        if dep.spec.replicas > 1:
            dep.spec.replicas = 1
            apps_api.patch_namespaced_deployment("web", "default", dep)
            print("⚠️ Low green score — scaled DOWN web deployment.")

    time.sleep(30)
