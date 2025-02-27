from fastapi import FastAPI
from core.gcloud import GCloud

app = FastAPI()
gcloud = GCloud(credential_path=("slt_auth_keys.json"))

@app.get("/hello")
def Hello():
    return {"status": "success", "message": "Hello World"}

@app.post("/start-server")
def start_server(zone, instance_name):
    return gcloud.start_instance(zone, instance_name)
    
@app.post("/end-server")
def stop_server(zone, instance_name):
    return gcloud.stop_instance(zone, instance_name)
    
@app.get("/server-status")
def server_status(zone, instance_name):
    return gcloud.get_instance_status(zone, instance_name)

@app.get("/list-server")
def list_server():
    result = []
    instances = gcloud.list_all_instances()
    for zone, instance in instances.items():
        for machine in instance:
            result.append({"Instance Name": machine.name, "Instance Status": machine.status, "Zone": zone})
    return result