from typing import Dict, Any

from fastapi import Depends, HTTPException
from fastapi import FastAPI, Response
from opensearchpy import OpenSearch
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel

from api.auth import authenticate_and_decode
from api.config import settings
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


@app.post("/search",
          summary="Returns search results the user has access to see",
          tags=["Endpoints"],
          description="Receives a JWT and a search term in the body, validates and decodes"
                      " the JWT to get the list of investigations the user can see, then adds them to a filter"
                      " in the opensearch query so we're only showing the user what they have access to see")
async def search_opensearch(
        request: SearchRequest,
        investigations: dict = Depends(authenticate_and_decode)
):
    endpoint_hits_counter.inc()

    # Extract all `id` values from the investigations list
    id_list = [inv['id'] for inv in investigations]

    # Create the custom filter using the list of IDs, i.e: custom_filter = {"terms": {"id": ["101", "103"]}}
    custom_filter = {"terms": {"id": id_list}}

    # Override any client-provided filters by setting the hard-coded filter
    if "bool" in request.query:
        # Replace the `filter` section with the hard-coded filter
        request.query["bool"]["filter"] = [custom_filter]
    else:
        # If there's no `bool` clause, create it with the filter and wrap the existing query in `must`
        request.query = {
            "bool": {
                "must": [request.query],
                "filter": [custom_filter]
            }
        }
    # Execute the modified query in OpenSearch
    try:
        response = opensearch_client.search(
            body={"query": request.query},
            index=settings.opensearch_index
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/version", summary="Returns the current version of the API", tags=["Endpoints"])
async def version():
    return {"version": settings.version}


@app.get("/metrics", summary="Returns Prometheus metrics for the application", tags=["Endpoints"])
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
