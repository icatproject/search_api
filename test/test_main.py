from fastapi.testclient import TestClient
from api.main import app
from api.config import settings
import jwt
from pathlib import Path
from api.logger import app_logger

# Initialize the test client
client = TestClient(app)

# Load private and public keys for JWT
PRIVATE_KEY_PATH = Path("test/jwt-key")
PUBLIC_KEY_PATH = Path("test/jwt-key.pub")

# Read private and public key contents
private_key = PRIVATE_KEY_PATH.read_text()
settings.jwt_public_key = PUBLIC_KEY_PATH.read_text()  # Set public key in settings

# Define the search request body
search_body = {
    "query": {
        "match": {
            "title": "Investigation"
        }
    }
}


def create_jwt(investigations):
    # Define the payload
    payload = {
        "sub": "1234567890",
        "name": "John Doe",
        "admin": True,
        "iat": 1516239022,
        "investigations": investigations
    }

    # Create a JWT with the RS256 algorithm and the private key
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


def test_search_with_valid_jwt():
    # Create a JWT with a sample investigation payload
    investigations = [{"id": "101"}, {"id": "103"}]
    token = create_jwt(investigations)

    # Send a POST request to the /search endpoint with the JWT in the Authorization header
    response = client.post(
        "/search",
        json=search_body,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check if the status code is 200 and response contains expected fields
    assert response.status_code == 200
    assert "hits" in response.json()  # Example assertion to verify search results are returned
    assert response.json()["hits"]["total"]["value"] > 0  # Ensure there are some results


def test_search_with_invalid_investigations():
    investigations = [{"id": "109"}, {"id": "108"}]
    token = create_jwt(investigations)

    response = client.post(
        "/search",
        json=search_body,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "hits" in response.json()
    assert response.json()["hits"]["total"]["value"] == 0


def test_search_with_no_investigations():
    payload = {
        "sub": "1234567890",
        "name": "John Doe",
        "admin": True,
        "iat": 1516239022
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")

    response = client.post(
        "/search",
        json=search_body,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "No investigations found in token"


def test_search_with_invalid_jwt():
    # Create an invalid JWT
    invalid_token = "invalid.token.string"

    response = client.post(
        "/search",
        json=search_body,
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "JWT validation failed with Scigateway-auth"


def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers[
               "content-type"] == "text/plain; version=0.0.4; charset=utf-8"  # Standard for Prometheus metrics
