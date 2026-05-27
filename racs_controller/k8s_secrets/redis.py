from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import v1
from constants import NAMESPACE

# --- Constants ---

SECRET_NAME = "redis"
SECRET_TYPE = "Opaque"
REDIS_PASSWORD_VALUE = ""


def deploy_redis_secret():
    manifest = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": SECRET_NAME, "namespace": NAMESPACE},
        "type": SECRET_TYPE,
        "stringData": {"REDIS_PASSWORD": REDIS_PASSWORD_VALUE},
    }

    safe_kube_call(
        v1.create_namespaced_secret,
        body=manifest,
        namespace=NAMESPACE,
        ignore_conflict=True,
    )


def delete_redis_secret():
    safe_kube_call(v1.delete_namespaced_secret, name=SECRET_NAME, namespace=NAMESPACE)
