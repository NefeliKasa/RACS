from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import app_v1
from constants import NAMESPACE, REDIS_HOST, REDIS_PORT, SESSION_TIMEOUT

# --- Constants ---

AWS_DEPLOYMENT_NAME = "aws-service"
AWS_CONTAINER_NAME = "aws-service"
AWS_LABEL = "aws-service"
AWS_IMAGE = "nefks/aws-service:latest"
JWT_SECRET_NAME = "jwt"
JWT_SECRET_KEY = "secret"
JWT_ALGORITHM_KEY = "algorithm"
SERVICE_TARGET_PORT = 80


def deploy_aws_service():
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": AWS_DEPLOYMENT_NAME,
            "namespace": NAMESPACE,
            "labels": {"app": AWS_LABEL},
        },
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": AWS_LABEL}},
            "template": {
                "metadata": {"labels": {"app": AWS_LABEL}},
                "spec": {
                    "containers": [
                        {
                            "name": AWS_CONTAINER_NAME,
                            "image": AWS_IMAGE,
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


def delete_aws_service():
    safe_kube_call(
        app_v1.delete_namespaced_deployment,
        name=AWS_DEPLOYMENT_NAME,
        namespace=NAMESPACE,
    )
