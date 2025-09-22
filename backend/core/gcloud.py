from pathlib import Path
from typing import Dict, List, Optional, Union
from googleapiclient import discovery
from google.oauth2 import service_account
from core.enums import InstanceStatus, OperationStatus, OperationType
from core.models import OperationData, OperationTimestamps, InstanceData, InstanceTimestamps

class GCloud:
    def __init__(self, credential_path: Union[str, Path]):
        self.credential_path = Path(credential_path)
        self.credentials = service_account.Credentials.from_service_account_file(self.credential_path)
        self.service = discovery.build('compute', 'v1', credentials=self.credentials)

    def list_all_instances(self, status: Optional[InstanceStatus] = None) -> Dict[str, List[InstanceData]]:
        """
        Lists all compute instances in all zones for a Google Cloud project, 
        abstracting zone management.

        Args:
            status (Optional[InstanceStatus]): Filter instances by status.

        Returns:
            Dict[str, List[InstanceData]]: A dictionary with zones as keys and a list of instances as values.
        """
        request = self.service.instances().aggregatedList(project=self.credentials.project_id)

        matches = {}
        
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
                                status=InstanceStatus(instance['status']),
                                zone=zone,
                                machineType=machine_type,
                                timestamps=InstanceTimestamps(
                                    creationTimestamp=instance['creationTimestamp'],
                                    deletionTimestamp=instance.get('deletionTimestamp'),
                                    lastStartTimestamp=instance.get('lastStartTimestamp'),
                                    lastStopTimestamp=instance.get('lastStopTimestamp')
                                )
                            )
                            instances = matches.get(zone, [])
                            instances.append(instance_data)
                            matches[zone] = instances
            
            request = self.service.instances().aggregatedList_next(previous_request=request, previous_response=response)

        return matches


    def start_instance(self, zone: str, instance_name: str) -> OperationData:
        """
        Starts a compute instance in a Google Cloud project.

        Args:
            zone (str): The zone of the instance.
            instance_name (str): The name of the instance.

        Returns:
            OperationData: The operation data.
        """
        request = self.service.instances().start(project=self.credentials.project_id, zone=zone, instance=instance_name)
        response = request.execute()

        return OperationData(
            name=response['name'],
            type=OperationType(response['operationType']),
            status=OperationStatus(response['status']),
            zone=zone,
            timestamps=OperationTimestamps(
                insertTime=response['insertTime'],
                startTime=response.get('startTime'),
                endTime=response.get('endTime')
            )
        )
    
    def get_instance_status(self, zone: str, instance_name: str) -> InstanceStatus:
        """
        Gets the status of a compute instance in a Google Cloud project.

        Args:
            zone (str): The zone of the instance.
            instance_name (str): The name of the instance.

        Returns:
            InstanceStatus: The status of the instance.
        """
        request = self.service.instances().get(project=self.credentials.project_id,
                                               zone=zone, instance=instance_name)
        response = request.execute()
        
        return InstanceStatus(response['status'])
    
    def stop_instance(self, zone: str, instance_name: str) -> OperationData:
        """
        Stops a compute instance in a Google Cloud project.

        Args:
            zone (str): The zone of the instance.
            instance_name (str): The name of the instance.

        Returns:
            OperationData: The operation data.
        """
        request = self.service.instances().stop(project=self.credentials.project_id,
                                                zone=zone, instance=instance_name)
        response = request.execute()
        
        return OperationData(
            name=response['name'],
            type=OperationType(response['operationType']),
            status=OperationStatus(response['status']),
            zone=zone,
            timestamps=OperationTimestamps(
                insertTime=response['insertTime'],
                startTime=response.get('startTime'),
                endTime=response.get('endTime')
            )
        )

    def get_operation_data(self, zone: str, operation_name: str) -> OperationData:
        """
        Gets the data of an operation in a Google Cloud project.

        Args:
            zone (str): The zone of the operation.
            operation_name (str): The name of the operation.

        Returns:
            OperationData: The operation data.
        """
        request = self.service.zoneOperations().get(project=self.credentials.project_id,
                                                    zone=zone, operation=operation_name)
        response = request.execute()

        return OperationData(
            name=response['name'],
            type=OperationType(response['operationType']),
            status=OperationStatus(response['status']),
            zone=zone,
            timestamps=OperationTimestamps(
                insertTime=response['insertTime'],
                startTime=response.get('startTime'),
                endTime=response.get('endTime')
            )
        )

    def get_instance_operations(self, zone: str, instance_name: str, status: Optional[OperationStatus] = None) -> List[OperationData]:
        """
        Gets the operations of a compute instance in a Google Cloud project.

        Supported operation types are in the OperationType enum.

        Args:
            zone (str): The zone of the instance.
            instance_name (str): The name of the instance.
            status (Optional[OperationStatus]): Filter operations by status. Defaults to [OperationStatus.RUNNING, OperationStatus.PENDING].

        Returns:
            List[OperationData]: A list of operation data.
        """
        if not status:
            status = [OperationStatus.RUNNING, OperationStatus.PENDING]

        if not isinstance(status, list):
            status = [status]

        status = [s.value for s in status]

        request = self.service.zoneOperations().list(
            project=self.credentials.project_id, zone=zone, 
            filter=f"targetLink eq https://www.googleapis.com/compute/v1/projects/{self.credentials.project_id}/zones/{zone}/instances/{instance_name}"
        )

        operations = []
        operation_types = [operation_type.value for operation_type in OperationType]
        
        while request is not None:
            response = request.execute()
            
            for operation in response.get('items', []):
                operation_type = operation['operationType']
                if (status is None or operation['status'] in status) and operation_type in operation_types:
                    operations.append(OperationData(
                        name=operation['name'],
                        type=OperationType(operation['operationType']),
                        status=OperationStatus(operation['status']),
                        zone=zone,
                        timestamps=OperationTimestamps(
                            insertTime=operation['insertTime'],
                            startTime=operation.get('startTime'),
                            endTime=operation.get('endTime')
                        )
                    ))
            
            request = self.service.zoneOperations().list_next(previous_request=request, previous_response=response)

        return operations