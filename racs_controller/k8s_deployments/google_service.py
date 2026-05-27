from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import app_v1
from constants import NAMESPACE, REDIS_HOST, REDIS_PORT, SESSION_TIMEOUT

# --- Constants ---

DEPLOYMENT_NAME = "google-service"
CONTAINER_NAME = "google-service"
LABEL = "google-service"
IMAGE = "nefks/google-service:latest"
JWT_SECRET_NAME = "jwt"
JWT_SECRET_KEY = "secret"
JWT_ALGORITHM_KEY = "algorithm"
SERVICE_TARGET_PORT = 80


def deploy_google_service():
    manifest = {
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
                                }
                            ],
                        }
                    ]
                },
            },
        },
    }

    safe_kube_call(
        app_v1.create_namespaced_deployment,
        body=manifest,
        namespace=NAMESPACE,
        ignore_conflict=True,
    )


def delete_google_service():
    safe_kube_call(
        app_v1.delete_namespaced_deployment, name=DEPLOYMENT_NAME, namespace=NAMESPACE
    )
