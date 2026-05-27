from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import app_v1
from constants import NAMESPACE, REDIS_HOST, REDIS_PORT, SESSION_TIMEOUT

# --- Constants ---

DEPLOYMENT_NAME = "racs-server"
CONTAINER_NAME = "racs-server-container"
LABEL = "racs-server"
IMAGE = "nefks/racs-server:latest"
CONFIG_MAP_NAME = "service-endpoints"
JWT_SECRET_NAME = "jwt"
JWT_SECRET_KEY = "secret"
JWT_ALGORITHM_KEY = "algorithm"
SERVICE_TARGET_PORT = 9376


class RacsServer:
    def __init__(self, selection_policy):
        self.selection_policy = selection_policy

    def _get_manifest(self):
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": DEPLOYMENT_NAME, "namespace": NAMESPACE},
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
                                "envFrom": [
                                    {
                                        "configMapRef": {
                                            "name": CONFIG_MAP_NAME
                                        }
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "JWT_SECRET",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": JWT_SECRET_NAME,
                                                "key": JWT_SECRET_KEY,
                                            }
                                        },
                                    },
                                    {
                                        "name": "JWT_ALGORITHM",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": JWT_SECRET_NAME,
                                                "key": JWT_ALGORITHM_KEY,
                                            }
                                        },
                                    },
                                    {
                                        "name": "REDIS_HOST",
                                        "value": REDIS_HOST,
                                    },
                                    {
                                        "name": "REDIS_PORT",
                                        "value": str(REDIS_PORT),
                                    },
                                    {
                                        "name": "SESSION_TIMEOUT",
                                        "value": str(SESSION_TIMEOUT),
                                    },
                                    {
                                        "name": "SELECTION_POLICY",
                                        "value": str(self.selection_policy),
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

    def patch(self, new_selection_policy):
        self.selection_policy = new_selection_policy
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
