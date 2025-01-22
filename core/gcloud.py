from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from googleapiclient import discovery
from google.oauth2 import service_account
from pydantic import BaseModel


class ComputeStatus(Enum):
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    TERMINATED = "TERMINATED"
    SUSPENDED = "SUSPENDED"
    STARTING = "STAGING"


class Timestamps(BaseModel):
    creationTimestamp: str
    deletionTimestamp: Optional[str]
    lastStartTimestamp: Optional[str]
    lastStopTimestamp: Optional[str]


class InstanceData(BaseModel):
    name: str
    status: ComputeStatus
    zone: str
    machineType: str
    timestamps: Timestamps


class GCloud:
    def __init__(self, credential_path: Union[str, Path]):
        self.credential_path = Path(credential_path)
        self.credentials = service_account.Credentials.from_service_account_file(self.credential_path)
        self.service = discovery.build('compute', 'v1', credentials=self.credentials)
        
    def list_all_instances(self, project_id: str, status: Optional[ComputeStatus] = None):
        """
        Lists all compute instances in all zones for a Google Cloud project, 
        abstracting zone management.

        Args:
            project_id (str): Your Google Cloud project ID.
            status (Optional[ComputeStatus]): Filter instances by status.
        """
        request = self.service.instances().aggregatedList(project=project_id)

        matches = defaultdict(list)
        
        while request is not None:
            response = request.execute()
            
            for zone, instances_in_zone in response.get('items', {}).items():
                if 'instances' in instances_in_zone:
                    for instance in instances_in_zone['instances']:
                        if status is None or instance['status'] == status.value:
                            if zone.startswith('zones/'):
                                zone = zone.split('/')[-1]
                            machine_type_split = "/machineTypes/"
                            if machine_type_split in instance["machineType"]:
                                machine_type = instance["machineType"].split(machine_type_split)[1]
                            
                            instance_data = InstanceData(
                                name=instance['name'],
                                status=ComputeStatus(instance['status']),
                                zone=zone,
                                machineType=machine_type,
                                timestamps=Timestamps(
                                    creationTimestamp=instance['creationTimestamp'],
                                    deletionTimestamp=instance.get('deletionTimestamp'),
                                    lastStartTimestamp=instance.get('lastStartTimestamp'),
                                    lastStopTimestamp=instance.get('lastStopTimestamp')
                                )
                            )
                            matches[zone].append(instance_data)
            
            request = self.service.instances().aggregatedList_next(previous_request=request, previous_response=response)

        return matches


    def start_instance(self, project_id: str, zone: str, instance_name: str):
        """
        Starts a compute instance in a Google Cloud project.

        Args:
            project_id (str): Your Google Cloud project ID.
            zone (str): The zone of the instance.
            instance_name (str): The name of the instance.
        """
        request = self.service.instances().start(project=project_id, zone=zone, instance=instance_name)
        response = request.execute()
        
        return response
    
    def get_status(self, project_id: str, zone: str, instance_name: str) -> ComputeStatus:
        """
        Gets the status of a compute instance in a Google Cloud project.

        Args:
            project_id (str): Your Google Cloud project ID.
            zone (str): The zone of the instance.
            instance_name (str): The name of the instance.
        """
        request = self.service.instances().get(project=project_id, zone=zone, instance=instance_name)
        response = request.execute()
        
        return ComputeStatus(response['status'])
    
    def stop_instance(self, project_id: str, zone: str, instance_name: str):
        """
        Stops a compute instance in a Google Cloud project.

        Args:
            project_id (str): Your Google Cloud project ID.
            zone (str): The zone of the instance.
            instance_name (str): The name of the instance.
        """
        request = self.service.instances().stop(project=project_id, zone=zone, instance=instance_name)
        response = request.execute()
        
        return response
