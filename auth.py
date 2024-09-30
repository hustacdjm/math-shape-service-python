from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

# Initialize a variable to hold the API token
API_TOKEN = None

api_key_header = APIKeyHeader(name="X-API-TOKEN")

def set_api_token(token: str):
    global API_TOKEN
    API_TOKEN = token

def verify_token(api_key: str = Depends(api_key_header)):
    if API_TOKEN is None:
        raise HTTPException(status_code=500, detail="API token not set")
    
    if api_key != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing API token")