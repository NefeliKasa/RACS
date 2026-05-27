from pydantic import BaseModel
from typing import Dict, Any


class AuthRequest(BaseModel):
    azure_credentials: Dict[str, str]
    google_credentials: Dict[str, str]
    aws_credentials: Dict[str, str]


class BaseBlobRequest(BaseModel):
    bucket: str
    key: str


class UploadBlobRequest(BaseBlobRequest):
    blob: str
