from typing import Dict, Any

from fastapi import FastAPI, Response, HTTPException
from fastapi.params import Depends
from opensearchpy import OpenSearch
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from api.config import settings
from api.investigations import extract_investigations
from api.check_jwt import check_jwt_exists, validate_jwt_with_scigateway_auth
from api.logger import app_logger

app = FastAPI(
    title="Search API",
    description=" Middleware that verifies a JWT, validates it against Scigateway auth, "
                "and filters search results from OpenSearch based on user permissions "
                "before returning authorised data to the client",
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
    query: Dict[str, Any]


@app.get("/search",
          summary="Returns search results the user has access to see",
          description="Receives a JWT and a search term in the url, validates and decodes"
                      " the JWT to get the list of investigations the user can see, then add to a filter"
                      " in the opensearch query so we're only showing the user what they have access to see")
async def search_opensearch(request: SearchRequest, token: str = Depends(check_jwt_exists)):
    endpoint_hits_counter.inc()

    # Validate the token with the third-party API (uncomment when implemented)
    # payload = validate_jwt_with_scigateway_auth(token)

    # Extract investigations from the validated payload
    # investigations = extract_investigations(payload)

    # TESTING: Hard-coded filter to apply to every request
    hard_coded_filter = {"terms": {"id": ["101", "103"]}}

    # Override any client-provided filters by setting the hard-coded filter
    if "bool" in request.query:
        # Replace the `filter` section with the hard-coded filter
        request.query["bool"]["filter"] = [hard_coded_filter]
    else:
        # If there's no `bool` clause, create it with the filter and wrap the existing query in `must`
        request.query = {
            "bool": {
                "must": [request.query],
                "filter": [hard_coded_filter]
            }
        }

    # Execute the modified query in OpenSearch
    try:
        response = opensearch_client.search(
            body={"query": request.query},
            index="my-index"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/version", summary="Returns the current version of the API")
async def version():
    return {"version": settings.version}


@app.get("/metrics", summary="Returns Prometheus metrics for the application")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
