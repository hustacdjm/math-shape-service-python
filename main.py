from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from routes import router  # Import the routes
from fastapi.responses import JSONResponse
import uvicorn
import signal
import os
import threading
import time
import sys
import logging
from auth import set_api_token, verify_token

# Create FastAPI instance
app = FastAPI()

# Define a route
@app.get("/status", dependencies=[Depends(verify_token)])
def read_root():
    return {"status": "OK"}

# Define a route
@app.get("/sayHello", dependencies=[Depends(verify_token)])
def read_root():
    return {"message": "Hello, World!"}


@app.post("/shutdown", dependencies=[Depends(verify_token)])
def shutdown():
    def shutdown_server():
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGINT)
    
    threading.Thread(target=shutdown_server).start()
    return {"message": "Server is shutting down..."}

# Include the router from routes.py
app.include_router(router)

if __name__ == "__main__":

    extra_args = sys.argv[1:]

    if "--key" in extra_args:
        key_index = extra_args.index("--key") + 1
        KEY = extra_args[key_index]
        set_api_token(KEY)

    logging.basicConfig(level=logging.INFO)
    logging.info("KEY:" + KEY)

    if KEY is None:
        sys.exit(1)
   
    uvicorn.run(app, host="0.0.0.0", port=8001)
