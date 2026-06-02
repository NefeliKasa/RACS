import os
import requests
import json
import time

# --- Configuration ---

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
BUCKET = os.getenv("TEST_BUCKET", "demo-bucket")
KEY = os.getenv("TEST_KEY", "demo-file.txt") 

AZURE_CREDENTIALS = json.loads(os.getenv("AZURE_CREDENTIALS", "{}"))
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS", "{}"))
AWS_CREDENTIALS = json.loads(os.getenv("AWS_CREDENTIALS", "{}"))

LOCAL_TXT_PATH = os.getenv("LOCAL_TXT_PATH", "test.txt")

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

    # Load text from local .txt file
    print(f"\n--- Loading Text from: {LOCAL_TXT_PATH} ---")
    try:
        with open(LOCAL_TXT_PATH, "r", encoding="utf-8") as f:
            original_text = f.read().strip()
        print(f"Successfully loaded {len(original_text)} characters.")
    except FileNotFoundError:
        print(f"Error: Could not find '{LOCAL_TXT_PATH}'. Please create it and try again.")
        return

    # b. PUT
    print("\n--- b. PUT ---")
    put_payload = {
        "bucket": BUCKET,
        "key": KEY,
        "blob": original_text,
    }
    resp = requests.post(f"{API_BASE_URL}/put", json=put_payload, headers=session_headers)
    resp.raise_for_status()
    print("Success! Blob uploaded:", resp.json())

    # c. GET
    print("\n--- c. GET ---")
    get_payload = {"bucket": BUCKET, "key": KEY}
    resp = requests.post(f"{API_BASE_URL}/get", json=get_payload, headers=session_headers)
    resp.raise_for_status()
    
    text_content = resp.json()["data"]
    print("Success! Retrieved data (first 1000 chars):", text_content[:1000] + "...")

    # d. UPDATE
    print("\n--- d. UPDATE ---")
    
    # Prepend the new sentence
    updated_text = "Updated text file. " + original_text

    update_payload = {
        "bucket": BUCKET,
        "key": KEY,
        "blob": updated_text,
    }
    resp = requests.post(f"{API_BASE_URL}/update", json=update_payload, headers=session_headers)
    resp.raise_for_status()
    print("Success! Blob updated:", resp.json())
    time.sleep(1)

    # e. GET (Updated)
    print("\n--- e. GET (Updated) ---")
    resp = requests.post(f"{API_BASE_URL}/get", json=get_payload, headers=session_headers)
    resp.raise_for_status()
    updated_text_content = resp.json()["data"]
    print("Success! Retrieved updated data (first 1000 chars):", updated_text_content[:1000] + "...")

    # f. DELETE
    print("\n--- f. DELETE ---")
    resp = requests.post(f"{API_BASE_URL}/delete", json=get_payload, headers=session_headers)
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