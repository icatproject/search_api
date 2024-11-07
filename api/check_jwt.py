import requests
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, Request

from api.config import settings


# Check if JWT exists in Authorization header
def check_jwt_exists(request: Request):
    authorization: str = request.headers.get("Authorization")

    # Check if the Authorization header contains a Bearer token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    # Extract the token from the header
    token = authorization.split(" ")[1]
    return token


# Validate JWT with third-party API
def validate_jwt_with_scigateway_auth(token: str):
    # Validate the token with the third-party API
    response = requests.get(settings.scigateway_auth, headers={"Authorization": f"Bearer {token}"})

    # Check if validation failed
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="JWT validation failed with third-party API")

    # If the token is valid, decode it locally using the SECRET_KEY and ALGORITHM
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algo])
        return payload  # Return the decoded payload
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid JWT token: {str(e)}")
