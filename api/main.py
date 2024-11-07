from fastapi import FastAPI, Response
from fastapi.params import Depends
from opensearchpy import OpenSearch
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from api.config import settings
from api.investigations import extract_investigations
from api.check_jwt import check_jwt_exists, validate_jwt_with_third_party
from api.logger import app_logger

app = FastAPI(
    title="Search API",
    description=" This API receives a JWT and a search term in the url, validates and decodes"
                " the JWT to get the list of investigations the user can see, then sdd this to the filter"
                " in the opensearch query so we're only showing the user what they have access to see",
    version=settings.version,
    contact={
        "name": "Alexander Kemp",
    }
)

app_logger.info("Application started")

# Define a global counter for endpoint hits
endpoint_hits_counter = Counter('endpoint_hits', 'Count of hits on the /search endpoint')

# OpenSearch client setup using values from config
opensearch_client = OpenSearch(
    hosts=[{'host': settings.opensearch_host, 'port': settings.opensearch_port}],
    http_compress=True
)


# Model for search request
class SearchRequest(BaseModel):
    query: str


# Search in OpenSearch with JWT-based filtering
@app.post("/api/search")
async def search_opensearch(request: SearchRequest, token: str = Depends(check_jwt_exists)):
    endpoint_hits_counter.inc()

    # Validate the token with the third-party API
    payload = validate_jwt_with_third_party(token)

    # Extract investigations from the validated payload
    investigations = extract_investigations(payload)

    # OpenSearch query
    search_query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"description": request.query}}
                ],
                "filter": [
                    {"terms": {"user": investigations}}
                ]
            }
        }
    }

    # Execute search in OpenSearch
    response = opensearch_client.search(
        body=search_query,
        index="my-index"
    )

    return response


@app.get("/version", summary="Get API version", description="Returns the current version of the API")
async def version():
    return {"version": settings.version}


@app.get("/metrics", summary="Get metrics", description="Returns Prometheus metrics for the application")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
