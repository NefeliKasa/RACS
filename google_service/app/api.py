import os
import uuid
import redis
import json
from typing import Dict
from fastapi import FastAPI, HTTPException, Depends
from model import AuthRequest, BaseBlobRequest, UploadBlobRequest
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT, decodeJWT
from google.auth_handler import Authenticator
from google.utils import Utils
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="Google Service API")

redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT", 6379))
session_timeout = int(os.getenv("SESSION_TIMEOUT", 3600))

# Redis key-value store for user sessions.
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

jwt_bearer = JWTBearer()


# --- Helper Functions ---


def get_session_utils(token: str = Depends(jwt_bearer)) -> Utils:
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

    return Utils(session_data)


# --- API Routes ---


@app.post("/login", tags=["Authentication"])
def login(request: AuthRequest):
    try:
        credentials = request.model_dump()

        # Create a dedicated Utils instance for each login.
        new_user_utils = Utils(credentials)

        # Validate credentials.
        new_user_utils.validate_credentials()
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

    session_id = str(uuid.uuid4())
    token = signJWT(session_id)

    try:
        redis_client.setex(session_id, session_timeout, json.dumps(credentials))
    except redis.RedisError as e:
        logger.error(f"Redis connection failed while saving session: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Could not create session.",
        )

    logger.info(f"User authenticated. Session created: {token}")
    return {"access_token": token}


@app.post("/get", tags=["Blob Operations"])
def get_blob(request: BaseBlobRequest, token: str = Depends(jwt_bearer)):
    utils = get_session_utils(token)

    try:
        blob_content = utils.get(request.bucket, request.blob_name)
        return {"data": blob_content}
    except Exception as e:
        logger.error(f"Failed to get blob {request.blob_name}: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Failed to get blob {request.blob_name}: {str(e)}"
        )


@app.post("/put", tags=["Blob Operations"])
def put_blob(request: UploadBlobRequest, token: str = Depends(jwt_bearer)):
    utils = get_session_utils(token)

    try:
        byte_data = json.dumps(request.blob).encode("utf-8")
        utils.put(byte_data, request.bucket, request.blob_name)

        logger.info(f"Blob {request.blob_name} uploaded successfully.")
        return {"message": "Blob uploaded successfully"}
    except Exception as e:
        logger.error(f"Failed to upload blob {request.blob_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/update", tags=["Blob Operations"])
def update_blob(request: UploadBlobRequest, token: str = Depends(jwt_bearer)):
    utils = get_session_utils(token)

    try:
        byte_data = json.dumps(request.blob).encode("utf-8")
        utils.update(byte_data, request.bucket, request.blob_name)

        logger.info(f"Blob {request.blob_name} updated successfully.")
        return {"message": "Blob updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update blob {request.blob_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@app.post("/delete", tags=["Blob Operations"])
def delete_blob(request: BaseBlobRequest, token: str = Depends(jwt_bearer)):
    utils = get_session_utils(token)

    try:
        utils.delete(request.bucket, request.blob_name)

        logger.info(f"Blob {request.blob_name} deleted successfully.")
        return {"message": "Blob deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete blob {request.blob_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.post("/logout", tags=["Authentication"])
def logout(token: str = Depends(jwt_bearer)):
    payload = decodeJWT(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    session_id = payload["sub"]

    try:
        keys_deleted = redis_client.delete(session_id)

        if keys_deleted == 0:
            raise HTTPException(status_code=401, detail="Session not found.")
    except redis.RedisError as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Could not process logout."
        )

    logger.info(f"Session {session_id} logged out successfully.")
    return {"message": "Logged out successfully"}
