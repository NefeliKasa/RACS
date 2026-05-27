from k8s_secrets.jwt import (
    deploy_jwt_secret,
    delete_jwt_secret,
)
from k8s_secrets.aws_auth import (
    deploy_aws_auth_secret,
    delete_aws_auth_secret,
)
from k8s_secrets.azure_auth import (
    deploy_azure_auth_secret,
    delete_azure_auth_secret,
)
from k8s_secrets.google_auth import (
    deploy_google_auth_secret,
    delete_google_auth_secret,
)
from k8s_secrets.redis import (
    deploy_redis_secret,
    delete_redis_secret,
)

from k8s_config_maps.service_endpoints import (
    deploy_service_endpoints_configmap,
    delete_service_endpoints_configmap,
)

from k8s_services.racs_service import (
    deploy_racs_service,
    delete_racs_service,
)
from k8s_services.codec_service import (
    deploy_codec_service,
    delete_codec_service,
)
from k8s_services.aws_service import (
    deploy_aws_service as deploy_aws_network_service,
    delete_aws_service as delete_aws_network_service,
)
from k8s_services.azure_service import (
    deploy_azure_service as deploy_azure_network_service,
    delete_azure_service as delete_azure_network_service,
)
from k8s_services.google_service import (
    deploy_google_service as deploy_google_network_service,
    delete_google_service as delete_google_network_service,
)
from k8s_services.redis import (
    deploy_redis_service,
    delete_redis_service,
)

from k8s_stateful_sets.redis import (
    deploy_redis,
    delete_redis,
)

from k8s_deployments.racs_server import RacsServer
from k8s_deployments.codec_service import CodecService
from k8s_deployments.aws_service import (
    deploy_aws_service,
    delete_aws_service,
)
from k8s_deployments.azure_service import (
    deploy_azure_service,
    delete_azure_service,
)
from k8s_deployments.google_service import (
    deploy_google_service,
    delete_google_service,
)


class RacsController:
    def __init__(self, racs_config):
        spec = racs_config["spec"]
        self.selection_policy = spec["selection_policy"]
        self.encoding_parameter_k = spec["encoding_parameter_k"]
        self.encoding_parameter_n = spec["encoding_parameter_n"]

        self.racs_server = RacsServer(selection_policy=self.selection_policy)
        self.codec_service = CodecService(
            encoding_parameter_k=self.encoding_parameter_k,
            encoding_parameter_n=self.encoding_parameter_n,
        )

        return

    def init_racs(self):
        # 1. Deploy Secrets
        deploy_jwt_secret()
        deploy_aws_auth_secret()
        deploy_azure_auth_secret()
        deploy_google_auth_secret()
        deploy_redis_secret()

        # 2. Deploy ConfigMaps
        deploy_service_endpoints_configmap()

        # 3. Deploy Services (Networking)
        deploy_racs_service()
        deploy_codec_service()
        deploy_aws_network_service()
        deploy_azure_network_service()
        deploy_google_network_service()
        deploy_redis_service()

        # 4. Deploy App Containers
        deploy_redis()
        self.racs_server.deploy()
        self.codec_service.deploy()
        deploy_aws_service()
        deploy_azure_service()
        deploy_google_service()

        return

    def patch_racs(self, racs_config):
        spec = racs_config["spec"]
        self.selection_policy = spec["selection_policy"]
        self.encoding_parameter_k = spec["encoding_parameter_k"]
        self.encoding_parameter_n = spec["encoding_parameter_n"]

        self.racs_server.patch(self.selection_policy)
        self.codec_service.patch(
            self.encoding_parameter_k, self.encoding_parameter_n
        )

        return

    def delete_racs(self):
        # 1. Delete Deployments
        delete_redis()
        self.racs_server.delete()
        self.codec_service.delete()
        delete_aws_service()
        delete_azure_service()
        delete_google_service()

        # 2. Delete Services
        delete_racs_service()
        delete_codec_service()
        delete_aws_network_service()
        delete_azure_network_service()
        delete_google_network_service()
        delete_redis_service()

        # 3. Delete ConfigMap
        delete_service_endpoints_configmap()

        # 4. Delete Secrets
        delete_jwt_secret()
        delete_aws_auth_secret()
        delete_azure_auth_secret()
        delete_google_auth_secret()
        delete_redis_secret()

        return
