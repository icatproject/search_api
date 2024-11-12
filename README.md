# Search API

[![CI](https://github.com/icatproject/search_api/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/icatproject/search_api/actions/workflows/main.yml)

The Search API is middleware that verifies a JWT, validates it against Scigateway auth, and filters search results 
from OpenSearch based on user permissions before returning authorised data to the client.

The OpenAPI spec can be found at `/docs`.

## JWT metadata
The API looks for the `investigations` tag in the decoded jwt metadata, it then uses this to apply a filter to the search results.

## Example Request
```commandline
curl --request GET \
  --url http://127.0.0.1:8000/search \
  --header 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidXNlciI6InVzZXIxIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMiwiaW52ZXN0aWdhdGlvbnMiOlt7ImlkIjoiMTAxIn1dfQ.bHJcGR9CEzxnahv3PaSyNw9m2gScHg1NAnVXTZlTlBpnYMAdPpkeWEoOr2R55Sp3bA_t9tVYIM0ROgz3rmteyCbVhKCKG9vLbdFGvVtaGqPvEwLGM4ADw-cEZZU1WDLYGJwEW84tzvufMvlf9mLxNy3jrlfBA_bWFjZiDZz16Wb80v2kTlPZagoqJZvw4GUv4dxXlFFxp04ZqUQIxchpWUlvnNeGnsaUfoMmwbAqxOuyGSAAcYNRNhz_RNFWYybAR-pZp_lGYAiox1xUGG_7X2cJBe71JDsDvTXKTLx5xuFJd6-5Eb15JbbB1k3AV8UQOiozBd-AMBNI4LEJvtPIeRtruyp1PEwTE0nnmhQtZ6vl32zpkwYS5vLlx5WvPCQF0C8EizhAcLs224RM958EV0MKuOHKz-Jcx9oLeIzmhIDpr-B-Aox_qil-bKenJnQh6BStuZhFY7N13KxRr99dVrtQQ0LQpP6boavjywrHkDw62Mfbwl3UngzABpQC4MSj' \
  --header 'Content-Type: application/json' \
  --header 'User-Agent: insomnia/9.3.3' \
  --data '{"query": {"bool": {"must": [{"match": {"title": "Investigation"}}]}}}'
```
The JSON `query` contains the OpenSearch query. 
The API acts as a pass-through, so it must match the OpenSearch specification [here](https://opensearch.org/docs/latest/query-dsl/).


## Example Response
The response is a standard Opensearch response:
```json
{
  "took":4,
  "timed_out":false,
  "_shards":
  {
    "total":1,
    "successful":1,
    "skipped":0,
    "failed":0
  },
  "hits":
  {
    "total": 
    {
      "value":1,
      "relation":"eq"
    },
    "max_score":0.18232156,
    "hits":
    [
      {
        "_index":"my-index",
        "_id":"1",
        "_score":0.18232156,
        "_source":
        {
          "title":"Sample Investigation 1",
          "id":"101",
          "description":"Details about investigation 1",
          "user":"user1"
        }
      }
    ]
  }
}

```