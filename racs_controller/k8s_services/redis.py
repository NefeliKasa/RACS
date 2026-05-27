from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import v1
from constants import NAMESPACE, REDIS_SERVICE_NAME, REDIS_PORT

# --- Constants ---

SERVICE_NAME = REDIS_SERVICE_NAME
SELECTOR_LABEL = "redis"
SERVICE_PORT = REDIS_PORT
TARGET_PORT = REDIS_PORT
CLUSTER_IP = "None"  


def deploy_redis_service():
    manifest = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": SERVICE_NAME, "namespace": NAMESPACE},
        "spec": {
            "clusterIP": CLUSTER_IP,
            "selector": {"app": SELECTOR_LABEL},
            "ports": [
                {"protocol": "TCP", "port": SERVICE_PORT, "targetPort": TARGET_PORT}
            ],
        },
    }

    safe_kube_call(
        v1.create_namespaced_service,
        body=manifest,
        namespace=NAMESPACE,
        ignore_conflict=True,
    )


def delete_redis_service():
    safe_kube_call(v1.delete_namespaced_service, name=SERVICE_NAME, namespace=NAMESPACE)
