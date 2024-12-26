from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def Hello():
    return {"status": "success", "message": "Hello World"}

@app.post("/start-server")
def start_server(status_code: int):
    if 400 <= status_code < 500 or 500 <= status_code < 600:
        return {"status": "failure", "message": "Failed to start virtual machine"}
    elif 200 <= status_code < 300:
        return {"status": "success", "message": "Starting virtual machine"}