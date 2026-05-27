from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import v1
from constants import NAMESPACE

# --- Constants ---

SECRET_NAME = "jwt"
SECRET_TYPE = "Opaque"
JWT_SECRET_VALUE = ""
JWT_ALGORITHM_VALUE = ""


def deploy_jwt_secret():
    manifest = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": SECRET_NAME, "namespace": NAMESPACE},
        "type": SECRET_TYPE,
        "stringData": {"secret": JWT_SECRET_VALUE, "algorithm": JWT_ALGORITHM_VALUE},
    }

    safe_kube_call(
        v1.create_namespaced_secret,
        body=manifest,
        namespace=NAMESPACE,
        ignore_conflict=True,
    )


def delete_jwt_secret():
    safe_kube_call(v1.delete_namespaced_secret, name=SECRET_NAME, namespace=NAMESPACE)
