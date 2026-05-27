from google.api_core.exceptions import Conflict
from google.auth_handler import Authenticator
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class Utils:
    authenticator: Authenticator

    def __init__(self, credentials):
        self.authenticator = Authenticator(credentials)

    def validate_credentials(self):
        storage_client = self.authenticator.storage_client
        
        try:
            list(storage_client.list_buckets(max_results=1))
            
            logger.info("Google Cloud Storage credentials are valid.")
        except Exception as e:
            logger.error(f"Invalid Google Cloud Storage credentials: {e}")
            raise

    def get(self, bucket, blob_name):
        if bucket is None or blob_name is None:
            logger.error("Container name and blob name must be provided.")
            raise ValueError("Container name and blob name must be provided.")

        storage_client = self.authenticator.storage_client    
        
        try:
            bucket = storage_client.bucket(bucket)
            blob = bucket.blob(blob_name)
            
            data = blob.download_as_string()
            return data
        except Exception as e:
            logger.error(f"Error downloading blob '{blob_name}' from bucket '{bucket}': {e}")
            raise

    def put(self, data, bucket, blob_name, content_type="application/octet-stream"):
        if bucket is None or blob_name is None:
            logger.error("Container name and blob name must be provided.")
            raise ValueError("Container name and blob name must be provided.")

        storage_client = self.authenticator.storage_client
        
        try:
            self._create_container_if_not_exists(storage_client, bucket)
            
            bucket = storage_client.bucket(bucket)
            blob = bucket.blob(blob_name)

            blob.upload_from_string(data, content_type=content_type)
        except Exception as e:
            logger.error(f"Error uploading blob '{blob_name}' to bucket '{bucket}': {e}")
            raise

    def update(self, data, bucket, blob_name, content_type="application/octet-stream"):
        if bucket is None or blob_name is None:
            logger.error("Container name and blob name must be provided.")
            raise ValueError("Container name and blob name must be provided.")

        storage_client = self.authenticator.storage_client
        
        try:
            bucket = storage_client.bucket(bucket)
            blob = bucket.blob(blob_name)

            blob.upload_from_string(data, content_type=content_type)
        except Exception as e:
            logger.error(f"Error updating blob '{blob_name}' in bucket '{bucket}': {e}")
            raise

    def delete(self, bucket, blob_name):
        if bucket is None or blob_name is None:
            logger.error("Container name and blob name must be provided.")
            raise ValueError("Container name and blob name must be provided.")

        storage_client = self.authenticator.storage_client    
        
        try:
            bucket = storage_client.bucket(bucket)
            blob = bucket.blob(blob_name)
            
            blob.delete()
        except Exception as e:
            logger.error(f"Error deleting blob '{blob_name}' from bucket '{bucket}': {e}")
            raise

    def _create_container_if_not_exists(self, storage_client, bucket):
        try:
            storage_client.create_bucket(bucket)
        except Conflict as e:
            logger.debug(f"bucket '{bucket}' already exists: {e}")
        except Exception as e:
            logger.error(f"Error creating bucket '{bucket}': {e}")
            raise
