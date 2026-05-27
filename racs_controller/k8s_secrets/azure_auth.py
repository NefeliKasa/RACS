from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import v1
from constants import NAMESPACE

# --- Constants ---

SECRET_NAME = "azure-auth"
NAMESPACE = NAMESPACE
SECRET_TYPE = "Opaque"
CREDENTIALS_FILE_NAME = "azure_credentials.json"

CREDENTIALS_JSON = """{
  "storage_account": "",
  "client_id": "",
  "tenant_id": "",
  "client_secret": ""
}"""


def deploy_azure_auth_secret():
    manifest = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": SECRET_NAME, "namespace": NAMESPACE},
        "type": SECRET_TYPE,
        "stringData": {CREDENTIALS_FILE_NAME: CREDENTIALS_JSON},
    }

    safe_kube_call(
        v1.create_namespaced_secret,
        body=manifest,
        namespace=NAMESPACE,
        ignore_conflict=True,
    )


def delete_azure_auth_secret():
    safe_kube_call(v1.delete_namespaced_secret, name=SECRET_NAME, namespace=NAMESPACE)
