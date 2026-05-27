import time
import jwt
from decouple import config

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM = config("JWT_ALGORITHM")
JWT_EXPIRATION_SECONDS = config("SESSION_TIMEOUT", cast=int)


def signJWT(session_id: str) -> str:
    payload = {"sub": session_id, "exp": time.time() + JWT_EXPIRATION_SECONDS}

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except jwt.PyJWTError as e:
        return None
