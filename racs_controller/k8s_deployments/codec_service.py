from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import app_v1
from constants import NAMESPACE

# --- Constants ---

DEPLOYMENT_NAME = "codec-service"
CONTAINER_NAME = "codec-service"
LABEL = "codec-service"
IMAGE = "nefks/codec-service:latest"
SERVICE_TARGET_PORT = 80


class CodecService:
    def __init__(self, encoding_parameter_k, encoding_parameter_n):
        self.encoding_parameter_k = encoding_parameter_k
        self.encoding_parameter_n = encoding_parameter_n

    def _get_manifest(self):
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": DEPLOYMENT_NAME,
                "namespace": NAMESPACE,
                "labels": {"app": LABEL},
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": LABEL}},
                "template": {
                    "metadata": {"labels": {"app": LABEL}},
                    "spec": {
                        "containers": [
                            {
                                "name": CONTAINER_NAME,
                                "image": IMAGE,
                                "imagePullPolicy": "Always",
                                "ports": [{"containerPort": SERVICE_TARGET_PORT}],
                                "env": [
                                    {
                                        "name": "ENCODING_PARAMETER_K",
                                        "value": str(self.encoding_parameter_k),
                                    },
                                    {
                                        "name": "ENCODING_PARAMETER_N",
                                        "value": str(self.encoding_parameter_n),
                                    },
                                ],
                            }
                        ]
                    },
                },
            },
        }

    def deploy(self):
        safe_kube_call(
            app_v1.create_namespaced_deployment,
            namespace=NAMESPACE,
            body=self._get_manifest(),
            ignore_conflict=True,
        )

    def patch(self, new_k, new_n):
        self.encoding_parameter_k = new_k
        self.encoding_parameter_n = new_n
        safe_kube_call(
            app_v1.patch_namespaced_deployment,
            name=DEPLOYMENT_NAME,
            namespace=NAMESPACE,
            body=self._get_manifest(),
        )

    def delete(self):
        safe_kube_call(
            app_v1.delete_namespaced_deployment,
            name=DEPLOYMENT_NAME,
            namespace=NAMESPACE,
        )
