from pydantic import BaseModel
from typing import Dict, Any, TypedDict


class EncodeRequest(BaseModel):
    data: str
    

class DecodeMetadataDict(TypedDict):
    blocknums: list[int]
    padding: list[int]


class DecodeRequest(BaseModel):
    encoded_data: list[str]
    metadata: DecodeMetadataDict