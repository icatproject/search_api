from fastapi import HTTPException


# Extract and validate investigations
def extract_investigations(payload: dict):
    investigations = payload.get("investigations")
    if investigations is None:
        raise HTTPException(status_code=403, detail="User not authorized to view investigations")
    return investigations
