from fastapi import FastAPI, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlmodel import Session
from api.utils import check_operation_status
from core.enums import OperationType
from api.schema import create_db_and_tables, ParentJob, ParentJobPublic, get_session
from core.gcloud import GCloud
import logging, gdown, os
from dotenv import load_dotenv

class RequestBody(BaseModel):
    zone: str
    instance_name: str
    
load_dotenv()
    
app = FastAPI()
gdown_id = os.environ.get("GCLOUD_SECRET")
gdown_url = f"https://drive.google.com/uc?id={gdown_id}"
gdown.download(gdown_url, "slt_auth_keys.json", quiet=False)

gcloud = GCloud(credential_path=("slt_auth_keys.json"))

logging.basicConfig(filename="app.log",level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/hello")
def Hello():
    return {"status": "success", "message": "Hello World"}

@app.post("/start-server", response_model=ParentJobPublic)
def start_server(body: RequestBody, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    operation = gcloud.start_instance(body.zone, body.instance_name)
    print(operation.status)
    print(type(operation.status))
    parentjob = ParentJob(name=body.instance_name, zone=body.zone,
                        status=operation.status, type=OperationType.START,
                        is_successful=False)
    session.add(parentjob)
    session.commit()
    session.refresh(parentjob)
    background_tasks.add_task(check_operation_status, body.zone, operation.name, parentjob)
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
    
    background_tasks.add_task(check_operation_status, body.zone, operation.name, parentjob)
    return parentjob
    
@app.get("/server-status")
def server_status(zone: str, instance_name: str):
    return gcloud.get_instance_status(zone, instance_name)

@app.get("/list-server")
def list_server():
    result = []
    instances = gcloud.list_all_instances()
    for zone, instance in instances.items():
        for machine in instance:
            result.append({"Instance Name": machine.name, "Instance Status": machine.status, "Zone": zone})
    return result

