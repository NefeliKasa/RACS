import json
import requests
from fastapi import HTTPException
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class Utils:
    @staticmethod
    def authenticate_service(
        service_name: str, service_url: str, credentials: dict
    ) -> str:
        response = requests.post(
            f"{service_url}/login", json=credentials
        )

        if response.status_code != 200:
            logger.error(f"{service_name} auth failed: {response.text}")
            raise HTTPException(
                status_code=401, detail=f"{service_name} authentication failed"
            )

        token = response.json().get("access_token")
        if not token:
            logger.error(f"{service_name} login succeeded but no token was provided.")
            raise HTTPException(
                status_code=500, detail="Authentication token missing from response"
            )

        return token

    @staticmethod
    def fetch_service_data(service_url: str, token: str, payload: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.post(f"{service_url}/get", json=payload, headers=headers)
        response.raise_for_status()

        body = json.loads(response.json().get("data"))
        logger.info(f"Received response from {service_url}: {body}")

        encoded_data = body.get("encoded_data")
        metadata = body.get("metadata")

        return {
            "encoded_data": encoded_data,
            "padding_size": metadata.get("padding_size"),
            "block_num": metadata.get("block_num"),
        }

    @staticmethod
    def put_service_data(
        service_url: str, token: str, payload: dict, overwrite: bool = False
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        if overwrite:
            response = requests.post(
                f"{service_url}/update", json=payload, headers=headers
            )
        else:
            response = requests.post(
                f"{service_url}/put", json=payload, headers=headers
            )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def delete_service_data(service_url: str, token: str, payload: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.post(f"{service_url}/delete", json=payload, headers=headers)
        response.raise_for_status()

        return response.json()
