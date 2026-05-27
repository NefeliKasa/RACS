from google.cloud import storage
from google.oauth2 import service_account
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class Authenticator:
    credential: service_account.Credentials
    storage_client: storage.Client
    def __init__(self, credentials):

        credentials_dict = credentials.copy()
        print(f"Received credentials: {credentials_dict}")
        
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        self.credential = credentials

        self.storage_client = storage.Client(credentials=credentials)