from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import app_v1
from constants import NAMESPACE, REDIS_PORT 

# --- Constants ---

REDIS_DEPLOYMENT_NAME = "redis"
REDIS_CONTAINER_NAME = "redis"
REDIS_LABEL = "redis"
REDIS_IMAGE = "redis:7.0"
REDIS_PASSWORD_SECRET_NAME = "redis"
REDIS_PASSWORD_SECRET_KEY = "REDIS_PASSWORD"
SERVICE_TARGET_PORT = REDIS_PORT

CPU_REQUEST = "100m"
CPU_LIMIT = "500m"
MEMORY_REQUEST = "50Mi"
MEMORY_LIMIT = "100Mi"

LP_COMMAND = ["sh", "-c", "redis-cli -a $(REDIS_PASSWORD) ping"]
LP_INITIAL_DELAY_SECONDS = 15
LP_PERIOD_SECONDS = 15
LP_TIMEOUT_SECONDS = 2
RP_COMMAND = ["sh", "-c", "redis-cli -a $(REDIS_PASSWORD) ping"]
RP_INITIAL_DELAY_SECONDS = 10
RP_PERIOD_SECONDS = 5
RP_TIMEOUT_SECONDS = 2

VOLUME_MOUNT_NAME = "redis-data"
VOLUME_MOUNT_PATH = "/data"
VOLUME_CLAIM_NAME = "redis-data"
ACCESS_MODES = ["ReadWriteOnce"]
STORAGE_REQUEST = "100Mi"
STORAGE_CLASS_NAME = "standard"


def deploy_redis():
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {
            "name": REDIS_DEPLOYMENT_NAME,
            "namespace": NAMESPACE,
            "labels": {"app": REDIS_LABEL},
        },
        "spec": {
            "serviceName": "redis",
            "replicas": 1,
            "selector": {"matchLabels": {"app": REDIS_LABEL}},
            "template": {
                "metadata": {"labels": {"app": REDIS_LABEL}},
                "spec": {
                    "containers": [
                        {
                            "name": REDIS_CONTAINER_NAME,
                            "image": REDIS_IMAGE,
                            "imagePullPolicy": "Always",
                            "ports": [{"containerPort": SERVICE_TARGET_PORT}],
                            "env": [
                                {
                                    "name": "REDIS_PASSWORD",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": REDIS_PASSWORD_SECRET_NAME,
                                            "key": REDIS_PASSWORD_SECRET_KEY,
                                        }
                                    },
                                },
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": CPU_REQUEST,
                                    "memory": MEMORY_REQUEST,
                                },
                                "limits": {"cpu": CPU_LIMIT, "memory": MEMORY_LIMIT},
                            },
                            "livenessProbe": {
                                "exec": {"command": LP_COMMAND},
                                "initialDelaySeconds": LP_INITIAL_DELAY_SECONDS,
                                "periodSeconds": LP_PERIOD_SECONDS,
                                "timeoutSeconds": LP_TIMEOUT_SECONDS,
                            },
                            "readinessProbe": {
                                "exec": {"command": RP_COMMAND},
                                "initialDelaySeconds": RP_INITIAL_DELAY_SECONDS,
                                "periodSeconds": RP_PERIOD_SECONDS,
                                "timeoutSeconds": RP_TIMEOUT_SECONDS,
                            },
                            "volumeMounts": [
                                {
                                    "name": VOLUME_MOUNT_NAME,
                                    "mountPath": VOLUME_MOUNT_PATH,
                                }
                            ],
                        }
                    ]
                },
            },
            "volumeClaimTemplates": [
                {
                    "metadata": {
                        "name": VOLUME_CLAIM_NAME,
                    },
                    "spec": {
                        "accessModes": ACCESS_MODES,
                        "resources": {"requests": {"storage": STORAGE_REQUEST}},
                        "storageClassName": STORAGE_CLASS_NAME,
                    },
                }
            ],
        },
    }

    safe_kube_call(
        app_v1.create_namespaced_stateful_set,
        body=manifest,
        namespace=NAMESPACE,
        ignore_conflict=True,
    )


def delete_redis():
    safe_kube_call(
        app_v1.delete_namespaced_stateful_set,
        name=REDIS_DEPLOYMENT_NAME,
        namespace=NAMESPACE,
    )
