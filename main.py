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
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
import time


# beat heart
url = "http://localhost:8080/v3/edu/AnyConnectClient/heartbeat"
WORKER_STATUS = "OK"

# Create FastAPI instance
app = FastAPI()


# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers
)

def send_heartbeat(payload, headers):
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print(f"Heartbeat sent successfully: {response.status_code}")
        else:
            print(f"Failed to send heartbeat: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending heartbeat: {e}")

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

    print("Extra arguments:", extra_args)

    KEY="localtest"
    if "--key" in extra_args:
        key_index = extra_args.index("--key") + 1
        KEY = extra_args[key_index]
        set_api_token(KEY)

    WORKER_ID=None
    if "--workerId" in extra_args:
        key_index = extra_args.index("--workerId") + 1
        WORKER_ID = extra_args[key_index]        

    logging.basicConfig(level=logging.INFO)
    logging.info("KEY:" + KEY)
    logging.info("WORKER_id:" + WORKER_ID)

    if KEY is None:
        sys.exit(1)
   
    payload = {
        "workerId": WORKER_ID, 
        "status": WORKER_STATUS
    }
    headers = {
        "Content-Type": "application/json",
        "X-API-TOKEN": KEY
    }

    # Create a scheduler that runs in the background
    scheduler = BackgroundScheduler()
    
    # Schedule the job to run every 20 seconds
    scheduler.add_job(send_heartbeat, 'interval', seconds=20, args=[payload, headers])
    
    # Start the scheduler
    scheduler.start()

    print("Heartbeat scheduler started, will not block the main thread.")

    uvicorn.run(app, host="0.0.0.0", port=0)
