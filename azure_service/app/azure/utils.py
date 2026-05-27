from azure.core.exceptions import ResourceExistsError
from azure.auth_handler import Authenticator
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class Utils:
    authenticator: Authenticator

    def __init__(self, credentials):
        self.authenticator = Authenticator(credentials)

    def validate_credentials(self):
        try:
            next(self.authenticator.blob_service_client.list_containers(results_per_page=1), None)
            logger.info("Azure Blob Storage credentials are valid.")
        except Exception as e:
            logger.error(f"Invalid Azure Blob Storage credentials: {e}")
            raise

    def get(self, container, blob_name):
        if container is None or blob_name is None:
            logger.error("Container and blob name must be provided.")
            raise ValueError("Container and blob name must be provided.")

        blob_client = self.authenticator.get_blob_client(container, blob_name)

        try:
            data = blob_client.download_blob().readall()
            return data
        except Exception as e:
            logger.error(
                f"Error downloading blob '{blob_name}' from container '{container}': {e}"
            )
            raise

    def put(self, data, container, blob_name):
        if container is None or blob_name is None:
            logger.error("Container and blob name must be provided.")
            raise ValueError("Container and blob name must be provided.")

        self._create_container_if_not_exists(container)

        blob_service_client = self.authenticator.blob_service_client
        blob_client = blob_service_client.get_blob_client(
            container=container, blob=blob_name
        )

        try:
            blob_client.upload_blob(data)
        except Exception as e:
            logger.error(
                f"Error uploading blob '{blob_name}' to container '{container}': {e}"
            )
            raise

    def update(self, data, container, blob_name):
        if container is None or blob_name is None:
            logger.error("Container and blob name must be provided.")
            raise ValueError("Container and blob name must be provided.")

        blob_client = self.authenticator.get_blob_client(container, blob_name)

        try:
            blob_client.upload_blob(data, overwrite=True)
        except Exception as e:
            logger.error(
                f"Error uploading blob '{blob_name}' to container '{container}': {e}"
            )
            raise

    def delete(self, container, blob_name):
        if container is None or blob_name is None:
            logger.error("Container and blob name must be provided.")
            raise ValueError("Container and blob name must be provided.")

        blob_client = self.authenticator.get_blob_client(container, blob_name)

        try:
            blob_client.delete_blob()
        except Exception as e:
            logger.error(
                f"Error deleting blob '{blob_name}' from container '{container}': {e}"
            )
            raise

    def _create_container_if_not_exists(self, container):
        try:
            self.authenticator.blob_service_client.create_container(container)
        except ResourceExistsError as e:
            logger.debug(f"Container '{container}' already exists: {e}")
        except Exception as e:
            logger.error(f"Error creating container '{container}': {e}")
            raise
