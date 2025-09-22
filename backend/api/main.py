import logging
from fastapi import FastAPI, BackgroundTasks, Depends,  UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from api.utils import check_operation_status
from core.enums import OperationType
from core.gcloud import GCloud
from api.schema import create_db_and_tables, ParentJob, ParentJobPublic, get_session
import tempfile, os

class RequestBody(BaseModel):
    zone: str
    instance_name: str
    receiver: str

app = FastAPI()

logging.basicConfig(filename="app.log",level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/hello")
def Hello():
    return {"status": "success", "message": "Hello World"}

gcloud = None

@app.post("/load_config")
def load_config(file: UploadFile = File(...)):
    global gcloud 
    if gcloud is None:
        raw = file.file.read()
        fd, path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(raw)
            gcloud = GCloud(credential_path=path)
        finally:
            try: os.remove(path)
            except OSError: pass

@app.post("/start-server", response_model=ParentJobPublic)
def start_server(body: RequestBody, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    operation = gcloud.start_instance(body.zone, body.instance_name)
    parentjob = ParentJob(name=body.instance_name, zone=body.zone,
                        status=operation.status, type=OperationType.START,
                        is_successful=False)
    session.add(parentjob)
    session.commit()
    session.refresh(parentjob)
    background_tasks.add_task(check_operation_status, body.zone, body.receiver, operation.name, parentjob)
    return ParentJobPublic.model_validate(parentjob)

@app.post("/end-server", response_model=ParentJobPublic) 
def stop_server(body: RequestBody, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    operation = gcloud.stop_instance(body.zone, body.instance_name)
    parentjob = ParentJob(name=body.instance_name, zone=body.zone,
                        status=operation.status, type=OperationType.STOP,
                        is_successful=False)
    session.add(parentjob)
    session.commit()
    session.refresh(parentjob)
    
    background_tasks.add_task(check_operation_status, body.zone, body.receiver, operation.name, parentjob)
    return parentjob
    
@app.get("/server-status")
def server_status(zone: str, instance_name: str):
    return gcloud.get_instance_status(zone, instance_name)

@app.get("/list-server")
def list_server():
    try:
        result = []
        instances = gcloud.list_all_instances()
        for zone, instance in instances.items():
            for machine in instance:
                result.append({"Instance Name": machine.name, "Instance Status": machine.status, "Zone": zone})
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Server error: {str(e)}")

