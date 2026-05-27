from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import v1
from constants import NAMESPACE

# --- Constants ---

CONFIG_MAP_NAME = "service-endpoints"
AZURE_SERVICE_URL = "http://azure-service.racs.svc.cluster.local:80"
GOOGLE_SERVICE_URL = "http://google-service.racs.svc.cluster.local:80"
AWS_SERVICE_URL = "http://aws-service.racs.svc.cluster.local:80"
CODEC_SERVICE_URL = "http://codec-service.racs.svc.cluster.local:80"


def deploy_service_endpoints_configmap():
    manifest = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": CONFIG_MAP_NAME, "namespace": NAMESPACE},
        "data": {
            "AZURE_SERVICE": AZURE_SERVICE_URL,
            "GOOGLE_SERVICE": GOOGLE_SERVICE_URL,
            "AWS_SERVICE": AWS_SERVICE_URL,
            "CODEC_SERVICE": CODEC_SERVICE_URL,
        },
    }

    safe_kube_call(
        v1.create_namespaced_config_map,
        body=manifest,
        namespace=NAMESPACE,
        ignore_conflict=True,
    )


def delete_service_endpoints_configmap():
    safe_kube_call(
        v1.delete_namespaced_config_map, name=CONFIG_MAP_NAME, namespace=NAMESPACE
    )
