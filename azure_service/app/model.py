from pydantic import BaseModel
from typing import Dict, Any, TypedDict


class AuthRequest(BaseModel):
    storage_account: str
    client_id: str
    tenant_id: str
    client_secret: str


class BaseBlobRequest(BaseModel):
    container: str
    blob_name: str


class MetadataDict(TypedDict):
    block_num: int
    padding_size: int


class BlobDataDict(TypedDict):
    encoded_data: str
    metadata: MetadataDict


class UploadBlobRequest(BaseBlobRequest):
    blob: BlobDataDict
