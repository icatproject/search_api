import jwt
import requests
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.config import settings
from api.logger import app_logger

# Define the security scheme to expect an Authorization header
security = HTTPBearer()


async def authenticate_and_decode(credentials: HTTPAuthorizationCredentials = Security(security)):

    token = credentials.credentials  # Extract the JWT from the Authorization header
    # Validate the token
    try:
        app_logger.info(f"Trying to validate JWT at {settings.scigateway_auth}")
        response = requests.post(settings.scigateway_auth, json={"token": token})
        # Check if validation failed
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="JWT validation failed with Scigateway-auth")

        # Decode the JWT
        payload = jwt.decode(token, settings.jwt_public_key, algorithms=[settings.jwt_algo])

        investigations = payload.get("investigations")
        if investigations is None:
            raise HTTPException(status_code=500, detail="No investigations found in token")

        return investigations  # Return the payload if the token is valid

    except HTTPException as e:
        # Re-raise HTTPException directly without modification
        app_logger.error(f"HTTPException {e}")
        raise e

    except Exception as e:
        # Raise all other exceptions as 500 Internal Server Error
        app_logger.error(f"Exception {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
