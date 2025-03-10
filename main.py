
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import signal
import os
import threading
import time
import sys
import logging
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
import time
import server


KEY="localtest"
# beat heart
WORKER_URL = "http://localhost:10701/v3/edu/AnyConnectClient/heartbeat"
WORKER_ID = "localtest"
WORKER_HOST=None
WORKER_IP = None
WORKER_NAME=None
WORKER_VERSION=None
WORKER_PORT=None
WORKER_ROUTE=None
WORKER_ROUTE_VERSION=None
WORKER_STATUS = "Active"

# Create FastAPI instance
app = FastAPI()

# Add CORS middleware if you're calling API from browser (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Important to allow 'x-api-key'
)

# Function to check API key
def get_api_key(x_api_key: str = Header(None)):
    if x_api_key != KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

def send_heartbeat():

    global WORKER_PORT  # Ensure that we're modifying the global variable

    payload = {
        "workerId": WORKER_ID, 
        "proxyhost": WORKER_HOST,
        "workerName": WORKER_NAME,
        "workerVersion": WORKER_VERSION,
        "port": WORKER_PORT,
        "route":WORKER_ROUTE,
        "routeVersion":WORKER_ROUTE_VERSION,        
        "status": WORKER_STATUS,
        "type": KEY
    }
    headers = {
        "Content-Type": "application/json",
        "X-API-TOKEN": KEY
    }
    try:
        response = requests.post(WORKER_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:            
            WORKER_PORT=response.text
            print(f"Heartbeat sent successfully: {response.status_code}, {response.text}")            
        else:
            print(f"Failed to send heartbeat: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending heartbeat: {e}")

# Define a route
@app.get("/status")
async def get_status(api_key: str = Depends(get_api_key)):
    return {"message": "Access granted to secure data!"}

# Define a route
@app.get("/sayHello")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/shutdown")
async def shutdown(api_key: str = Depends(get_api_key)):
    def shutdown_server():
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGINT)
    
    threading.Thread(target=shutdown_server).start()
    return {"message": "Server is shutting down..."}

@app.get("/items")
async def get_items(api_key: str = Depends(get_api_key)):
    return server.get_items()


if __name__ == "__main__":

    extra_args = sys.argv[1:]

    print("Extra arguments:", extra_args)

    
    if "--key" in extra_args:
        key_index = extra_args.index("--key") + 1
        KEY = extra_args[key_index]

    if "--workerId" in extra_args:
        key_index = extra_args.index("--workerId") + 1
        WORKER_ID = extra_args[key_index]        
    if "--workerHost" in extra_args:
        key_index = extra_args.index("--workerHost") + 1
        WORKER_HOST = extra_args[key_index]        
    if "--workerName" in extra_args:
        key_index = extra_args.index("--workerName") + 1
        WORKER_NAME = extra_args[key_index]        
    if "--workerVersion" in extra_args:
        key_index = extra_args.index("--workerVersion") + 1
        WORKER_VERSION = extra_args[key_index]        
    if "--workerPort" in extra_args:
        key_index = extra_args.index("--workerPort") + 1
        WORKER_PORT = extra_args[key_index]        
    if "--workerRoute" in extra_args:
        key_index = extra_args.index("--workerRoute") + 1
        WORKER_ROUTE = extra_args[key_index]        
    if "--workerRouteVersion" in extra_args:
        key_index = extra_args.index("--workerRouteVersion") + 1
        WORKER_ROUTE_VERSION = extra_args[key_index]        

    logging.basicConfig(level=logging.INFO)
    logging.info("KEY:" + KEY)
    logging.info("WORKER_id:" + WORKER_ID)

    if KEY != 'localtest':
        # Create a scheduler that runs in the background
        scheduler = BackgroundScheduler()
    
        # Schedule the job to run every 20 seconds
        scheduler.add_job(send_heartbeat, 'interval', seconds=20)

        # Start the scheduler
        scheduler.start()

        print("Heartbeat scheduler started, will not block the main thread.")
   
    uvicorn.run(app, host="0.0.0.0", port=0)


