import os
import requests
import json
import time

# --- Configuration ---

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
BUCKET = os.getenv("TEST_BUCKET", "demo-bucket")
KEY = os.getenv("TEST_KEY", "demo-file.txt")

AZURE_CREDENTIALS = json.loads(os.getenv("AZURE_CREDENTIALS"))
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
AWS_CREDENTIALS = json.loads(os.getenv("AWS_CREDENTIALS"))


# --- Demo Implementation ---


def main():
    print(f"Starting demo for API: {API_BASE_URL}")

    session_headers = {"Content-Type": "application/json"}

    # a. LOGIN
    print("\n--- a. LOGIN ---")

    login_payload = {
        "azure_credentials": AZURE_CREDENTIALS,
        "google_credentials": GOOGLE_CREDENTIALS,
        "aws_credentials": AWS_CREDENTIALS,
    }

    resp = requests.post(f"{API_BASE_URL}/login", json=login_payload)
    resp.raise_for_status()

    token = resp.json().get("access_token")

    print(f"Success! Acquired Token: {token}")

    session_headers["Authorization"] = f"Bearer {token}"

    # b. PUT
    print("\n--- b. PUT ---")

    put_payload = {
        "bucket": BUCKET,
        "key": KEY,
        "blob": "This is the original data payload for the demo.",
    }
    resp = requests.post(
        f"{API_BASE_URL}/put", json=put_payload, headers=session_headers
    )
    resp.raise_for_status()

    print("Success! Blob uploaded:", resp.json())
    time.sleep(60) # Sleep to show the blob in the storage console before it gets updated/deleted in the next steps.

    # c. GET
    print("\n--- c. GET ---")

    get_payload = {"bucket": BUCKET, "key": KEY}
    resp = requests.post(
        f"{API_BASE_URL}/get", json=get_payload, headers=session_headers
    )
    resp.raise_for_status()

    print("Success! Retrieved data:", resp.json())

    # d. UPDATE
    print("\n--- d. UPDATE ---")

    update_payload = {
        "bucket": BUCKET,
        "key": KEY,
        "blob": "This is the UPDATED data payload for the demo.",
    }
    resp = requests.post(
        f"{API_BASE_URL}/update", json=update_payload, headers=session_headers
    )
    resp.raise_for_status()

    print("Success! Blob updated:", resp.json())
    time.sleep(1)

    # e. GET
    print("\n--- e. GET (Updated) ---")

    resp = requests.post(
        f"{API_BASE_URL}/get", json=get_payload, headers=session_headers
    )
    resp.raise_for_status()

    print("Success! Retrieved updated data:", resp.json())

    # f. DELETE
    print("\n--- f. DELETE ---")

    resp = requests.post(
        f"{API_BASE_URL}/delete", json=get_payload, headers=session_headers
    )
    resp.raise_for_status()

    print("Success! Blob deleted:", resp.json())

    # g. LOGOUT
    print("\n--- g. LOGOUT ---")

    resp = requests.post(f"{API_BASE_URL}/logout", headers=session_headers)
    resp.raise_for_status()

    print("Success! Logged out:", resp.json())

    print("\nDemo completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as e:
        print(f"\nAPI Request Failed: {e}")
        if e.response is not None:
            print(f"Response body: {e.response.text}")
