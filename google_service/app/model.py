from pydantic import BaseModel
from typing import Dict, Any, TypedDict


class AuthRequest(BaseModel):
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: str


class BaseBlobRequest(BaseModel):
    bucket: str
    blob_name: str

    
class MetadataDict(TypedDict):
    block_num: int
    padding_size: int


class BlobDataDict(TypedDict):
    encoded_data: str
    metadata: MetadataDict


class UploadBlobRequest(BaseBlobRequest):
    blob: BlobDataDict

