from fastapi import APIRouter, Depends
from auth import verify_token
import server

router = APIRouter()

@router.get("/items", dependencies=[Depends(verify_token)])
def getItems():
    return server.get_items()

@router.get("/wordSearch/{word}/{token}", dependencies=[Depends(verify_token)])
def wordSearch(word: str, token: str):
    return {"status": "OK", "searched_word": word, "token_verified": token}
