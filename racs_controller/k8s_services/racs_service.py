from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import v1
from constants import NAMESPACE

# --- Constants ---
SERVICE_NAME = "racs-service"
SERVICE_TYPE = "NodePort"
SELECTOR_LABEL = "racs-server"
SERVICE_PORT = 80
TARGET_PORT = 9376
NODE_PORT = 30001


def deploy_racs_service():
    manifest = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": SERVICE_NAME, "namespace": NAMESPACE},
        "spec": {
            "type": SERVICE_TYPE,
            "selector": {"app": SELECTOR_LABEL},
            "ports": [
                {
                    "protocol": "TCP",
                    "port": SERVICE_PORT,
                    "targetPort": TARGET_PORT,
                    "nodePort": NODE_PORT,
                }
            ],
        },
    }

    safe_kube_call(
        v1.create_namespaced_service,
        body=manifest,
        namespace=NAMESPACE,
        ignore_conflict=True,
    )


def delete_racs_service():
    safe_kube_call(
        v1.delete_namespaced_service,
        name=SERVICE_NAME,
        namespace=NAMESPACE,
    )
