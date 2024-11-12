import requests
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, Request

from api.config import settings


# Check if JWT exists in Authorisation header
def check_jwt_exists(request: Request):
    authorization: str = request.headers.get("Authorization")

    # Check if the Authorization header contains a Bearer token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    # Extract the token from the header
    token = authorization.split(" ")[1]
    return token


def validate_jwt_with_scigateway_auth(token: str):
    try:
        response = requests.post(
            settings.scigateway_auth,
            json={"token": token}
        )
        # Check if validation failed
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="JWT validation failed with Scigateway-auth")

        return response  # Or return relevant data from response if needed

    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        raise HTTPException(status_code=500, detail=f"Error communicating with Scigateway-auth: {str(e)}")


def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_public_key, algorithms=[settings.jwt_algo])
        return payload  # Return the decoded payload

    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Could not decode JWT token: {str(e)}")