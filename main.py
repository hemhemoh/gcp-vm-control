from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def Hello():
    return {"status": "success", "message": "Hello World"}