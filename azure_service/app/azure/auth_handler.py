from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class Authenticator:
    credential: ClientSecretCredential
    blob_service_client: BlobServiceClient

    def __init__(self, credentials):

        credentials_dict = credentials.copy()
        storage_account = credentials_dict.pop("storage_account", None)

        credential = ClientSecretCredential(**credentials_dict)
        self.credential = credential

        account_url = f"https://{storage_account}.blob.core.windows.net"

        self.blob_service_client = BlobServiceClient(
            account_url=account_url, credential=credential
        )

    def get_container_client(self, container):
        return self.blob_service_client.get_container_client(container)

    def get_blob_client(self, container, blob_name):
        container_client = self.get_container_client(container)
        return container_client.get_blob_client(blob_name)
