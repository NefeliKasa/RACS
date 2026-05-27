from pydantic import BaseModel
from typing import Dict, Any, TypedDict


class AuthRequest(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str


class BaseObjectRequest(BaseModel):
    bucket: str
    key: str


class MetadataDict(TypedDict):
    block_num: int
    padding_size: int


class ObjectDataDict(TypedDict):
    encoded_data: str
    metadata: MetadataDict


class UploadObjectRequest(BaseObjectRequest):
    object: ObjectDataDict
