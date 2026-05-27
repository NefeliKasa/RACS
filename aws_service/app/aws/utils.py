from aws.auth_handler import Authenticator
from utils.logging_config import setup_logger
from botocore.exceptions import ClientError

logger = setup_logger(__name__)


class Utils:
    authenticator: Authenticator

    def __init__(self, credentials):
        self.authenticator = Authenticator(credentials)

    def validate_credentials(self):
        try:
            s3_client = self.authenticator.s3_client
            s3_client.list_buckets()
            logger.info("AWS S3 credentials are valid.")
        except Exception as e:
            logger.error(f"Invalid AWS S3 credentials: {e}")
            raise

    def get(self, bucket, key):
        if bucket is None or key is None:
            logger.error("Bucket and object key must be provided.")
            raise ValueError("Bucket and object key must be provided.")

        s3_client = self.authenticator.s3_client

        try:
            response = s3_client.get_object(Bucket=bucket, Key=key)
            
            with response["Body"] as stream:
                data = stream.read()
            return data
        except Exception as e:
            logger.error(
                f"Error getting object '{key}' from bucket '{bucket}': {e}"
            )
            raise

    def put(self, data, bucket, key):
        if bucket is None or key is None:
            logger.error("Bucket and object key must be provided.")
            raise ValueError("Bucket and object key must be provided.")

        self._create_bucket_if_not_exists(bucket)

        s3_client = self.authenticator.s3_client

        try:
            s3_client.put_object(Bucket=bucket, Key=key, Body=data)
        except Exception as e:
            logger.error(
                f"Error uploading object '{key}' to bucket '{bucket}': {e}"
            )
            raise

    def update(self, data, bucket, key):
        if bucket is None or key is None:
            logger.error("Bucket and object key must be provided.")
            raise ValueError("Bucket and object key must be provided.")

        s3_client = self.authenticator.s3_client

        try:
            s3_client.put_object(Bucket=bucket, Key=key, Body=data)
        except Exception as e:
            logger.error(
                f"Error updating object '{key}' in bucket '{bucket}': {e}"
            )
            raise

    def delete(self, bucket, key):
        if bucket is None or key is None:
            logger.error("Bucket and object key must be provided.")
            raise ValueError("Bucket and object key must be provided.")

        s3_client = self.authenticator.s3_client

        try:
            s3_client.delete_object(Bucket=bucket, Key=key)
        except Exception as e:
            logger.error(
                f"Error deleting object '{key}' from bucket '{bucket}': {e}"
            )
            raise

    def _create_bucket_if_not_exists(self, bucket):
        try:
            self.authenticator.s3_client.head_bucket(Bucket=bucket)
            return 
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                pass 
        
        try:
            if self.authenticator.s3_client.meta.region_name == 'us-east-1':
                self.authenticator.s3_client.create_bucket(Bucket=bucket)
            else:
                self.authenticator.s3_client.create_bucket(
                    Bucket=bucket,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.authenticator.s3_client.meta.region_name
                    }
                )
            
        except Exception as e:
            logger.error(f"Error creating bucket '{bucket}': {e}")
            raise
