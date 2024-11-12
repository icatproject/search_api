import jwt
import requests
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.config import settings

# Define the security scheme to expect an Authorization header
security = HTTPBearer()


async def authenticate_and_decode(credentials: HTTPAuthorizationCredentials = Security(security)):

    token = credentials.credentials  # Extract the JWT from the Authorization header
    # Validate the token
    try:
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

    except Exception as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=f"Authentication error: {str(e)}"
        )
    