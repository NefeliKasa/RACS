from boto3 import client, Session
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class Authenticator:

    def __init__(self, credentials):
        self.s3_client = client(
            "s3",
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"],
            region_name=credentials["region_name"],
        )
