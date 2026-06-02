import os
import uuid
import random
import requests
import redis
import json
from typing import Dict, Tuple
from fastapi import FastAPI, HTTPException, Depends
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT, decodeJWT
from model import AuthRequest, BaseBlobRequest, UploadBlobRequest
from authenticator import Authenticator
from service_utils import Utils
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="RACS Service API")

# Global fields that will be used across the application.
azure_service = os.getenv("AZURE_SERVICE")
google_service = os.getenv("GOOGLE_SERVICE")
aws_service = os.getenv("AWS_SERVICE")
codec_service = os.getenv("CODEC_SERVICE")

redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT", 6379))
session_timeout = int(os.getenv("SESSION_TIMEOUT", 3600))

# Redis key-value store for user sessions.
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

jwt_bearer = JWTBearer()


# --- Helper Functions ---


def _get_session_authenticator(token: str = Depends(jwt_bearer)) -> Authenticator:
    """Gets the Authenticator instance associated with the current session based on the provided JWT token."""
    payload = decodeJWT(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    session_id = payload["sub"]

    try:
        session_data_json = redis_client.get(session_id)
        if not session_data_json:
            raise HTTPException(status_code=401, detail="Session not found or expired.")
    except redis.RedisError as e:
        logger.error(f"Failed to retrieve session data for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Could not retrieve session data.",
        )

    session_data = json.loads(session_data_json)

    return Authenticator(
        azure_auth_token=session_data["azure_auth_token"],
        google_auth_token=session_data["google_auth_token"],
        aws_auth_token=session_data["aws_auth_token"],
    )


# --- API Routes ---


@app.post("/login", tags=["Authentication"])
def login(request: AuthRequest):
    try:
        azure_token = Utils.authenticate_service(
            "Azure", azure_service, request.azure_credentials
        )
        google_token = Utils.authenticate_service(
            "Google", google_service, request.google_credentials
        )

        aws_token = Utils.authenticate_service(
            "AWS", aws_service, request.aws_credentials
        )

        session_id = str(uuid.uuid4())
        token = signJWT(session_id)

        session_data = {
            "azure_auth_token": azure_token,
            "google_auth_token": google_token,
            "aws_auth_token": aws_token,
        }

        try:
            redis_client.setex(session_id, session_timeout, json.dumps(session_data))
        except redis.RedisError as e:
            logger.error(f"Failed to store session data: {e}")
            raise HTTPException(status_code=500, detail="Failed to create session")

        logger.info(f"User authenticated. Session created: {token}")
        return {"access_token": token}
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@app.post("/get", tags=["Blob Operations"])
def get_blob(request: BaseBlobRequest, token: str = Depends(jwt_bearer)):
    authenticator = _get_session_authenticator(token)

    bucket = request.bucket
    key = request.key

    providers = ["azure", "google", "aws"]

    k = 2
    random_providers = random.sample(providers, k)

    encoded_data = []
    blocknums = []
    padding = []

    for i, provider in enumerate(random_providers):
        if provider == "azure":
            azure_results = Utils.fetch_service_data(
                service_url=azure_service,
                token=authenticator.azure_auth_token,
                payload={
                    "container": bucket,
                    "blob_name": key,
                },
            )

            encoded_data.append(azure_results["encoded_data"])
            blocknums.append(azure_results["block_num"])
            padding.append(azure_results["padding_size"])

        elif provider == "google":
            google_results = Utils.fetch_service_data(
                service_url=google_service,
                token=authenticator.google_auth_token,
                payload={
                    "bucket": bucket,
                    "blob_name": key,
                },
            )

            encoded_data.append(google_results["encoded_data"])
            blocknums.append(google_results["block_num"])
            padding.append(google_results["padding_size"])

        elif provider == "aws":
            aws_results = Utils.fetch_service_data(
                service_url=aws_service,
                token=authenticator.aws_auth_token,
                payload={
                    "bucket": bucket,
                    "key": key,
                },
            )

            encoded_data.append(aws_results["encoded_data"])
            blocknums.append(aws_results["block_num"])
            padding.append(aws_results["padding_size"])

    decode_service_response = requests.post(
        f"{codec_service}/decode",
        json={
            "encoded_data": encoded_data,
            "metadata": {
                "blocknums": blocknums,
                "padding": padding,
            },
        },
        headers={"Content-Type": "application/json"},
    )
    decode_service_response.raise_for_status()

    decoded_data = decode_service_response.json().get("decoded_data")
    logger.info(f"Decoded data retrieved successfully: {str(decoded_data)[:100]}...")

    return {"data": decoded_data}


@app.post("/put", tags=["Blob Operations"])
def put_blob(request: UploadBlobRequest, token: str = Depends(jwt_bearer)):
    authenticator = _get_session_authenticator(token)

    bucket = request.bucket
    key = request.key
    blob = request.blob

    encode_service_response = requests.post(
        f"{codec_service}/encode",
        json={"data": blob},
        headers={"Content-Type": "application/json"},
    )
    encode_service_response.raise_for_status()

    encoded_data_metadata = encode_service_response.json()["encoded_data_metadata"]
    if not encoded_data_metadata:
        raise HTTPException(status_code=500, detail="Encoding service returned no data")

    providers = ["azure", "google", "aws"]
    payload = {}
    for i, provider in enumerate(providers):
        if provider == "azure":
            payload = {
                "container": bucket,
                "blob_name": key,
                "blob": encoded_data_metadata[i],
            }

            azure_results = Utils.put_service_data(
                service_url=azure_service,
                token=authenticator.azure_auth_token,
                payload=payload,
            )

        elif provider == "google":
            payload = {
                "bucket": bucket,
                "blob_name": key,
                "blob": encoded_data_metadata[i],
            }

            google_results = Utils.put_service_data(
                service_url=google_service,
                token=authenticator.google_auth_token,
                payload=payload,
            )

        elif provider == "aws":
            payload = {
                "bucket": bucket,
                "key": key,
                "object": encoded_data_metadata[i],
            }

            aws_results = Utils.put_service_data(
                service_url=aws_service,
                token=authenticator.aws_auth_token,
                payload=payload,
            )

        logger.info(f"Putting data shard to {provider}: {str(payload)[:100]}...")

    return {"message": "Blob uploaded successfully"}


@app.post("/update", tags=["Blob Operations"])
def update_blob(request: UploadBlobRequest, token: str = Depends(jwt_bearer)):
    authenticator = _get_session_authenticator(token)

    bucket = request.bucket
    key = request.key
    blob = request.blob

    encode_service_response = requests.post(
        f"{codec_service}/encode",
        json={"data": blob},
        headers={"Content-Type": "application/json"},
    )
    encode_service_response.raise_for_status()

    encoded_data_metadata = encode_service_response.json()["encoded_data_metadata"]
    if not encoded_data_metadata:
        raise HTTPException(status_code=500, detail="Encoding service returned no data")

    providers = ["azure", "google", "aws"]
    payload = {}
    for i, provider in enumerate(providers):
        if provider == "azure":
            payload = {
                "container": bucket,
                "blob_name": key,
                "blob": encoded_data_metadata[i],
            }
            
            azure_results = Utils.put_service_data(
                service_url=azure_service,
                token=authenticator.azure_auth_token,
                payload=payload,
                overwrite=True,
            )

        elif provider == "google":
            payload = {
                "bucket": bucket,
                "blob_name": key,
                "blob": encoded_data_metadata[i],
            }
            
            google_results = Utils.put_service_data(
                service_url=google_service,
                token=authenticator.google_auth_token,
                payload=payload,
                overwrite=True,
            )

        elif provider == "aws":
            payload = {
                "bucket": bucket,
                "key": key,
                "object": encoded_data_metadata[i],
            }
            
            aws_results = Utils.put_service_data(
                service_url=aws_service,
                token=authenticator.aws_auth_token,
                payload=payload,
                overwrite=True,
            )

        logger.info(f"Updating data shard to {provider}: {str(payload)[:100]}...")

    return {"message": "Blob updated successfully"}


@app.post("/delete", tags=["Blob Operations"])
def delete_blob(request: BaseBlobRequest, token: str = Depends(jwt_bearer)):
    authenticator = _get_session_authenticator(token)

    bucket = request.bucket
    key = request.key

    providers = ["azure", "google", "aws"]
    for i, provider in enumerate(providers):
        if provider == "azure":
            azure_results = Utils.delete_service_data(
                service_url=azure_service,
                token=authenticator.azure_auth_token,
                payload={
                    "container": bucket,
                    "blob_name": key,
                },
            )

        elif provider == "google":
            google_results = Utils.delete_service_data(
                service_url=google_service,
                token=authenticator.google_auth_token,
                payload={
                    "bucket": bucket,
                    "blob_name": key,
                },
            )

        elif provider == "aws":
            aws_results = Utils.delete_service_data(
                service_url=aws_service,
                token=authenticator.aws_auth_token,
                payload={
                    "bucket": bucket,
                    "key": key,
                },
            )

    return {"google": google_results, "azure": azure_results, "aws": aws_results}


@app.post("/logout", tags=["Authentication"])
def logout(token: str = Depends(jwt_bearer)):
    payload = decodeJWT(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    session_id = payload["sub"]

    try:
        keys_deleted = redis_client.delete(session_id)

        if keys_deleted == 0:
            raise HTTPException(
                status_code=401, detail="Session not found or already expired."
            )
    except redis.RedisError as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Could not process logout."
        )

    logger.info(f"Session {session_id} logged out successfully.")
    return {"message": "Logged out successfully"}
