import sys
from ..modules import util
from .genlauncher import Status, LogType
import boto3
import re

class spec():
    eks_client = None
    cluster = None
    data = None

    # Abstract
    @classmethod
    def get_instance(cls):
        cls.set_status(Status.GET_INST, "Retrieving cluster")
        cls.eks_client = boto3.client('eks')
        clusters = eks_client.list_clusters()["clusters"]
        re_pattern = util.read(cls.config, "eks", "Name")
        
        matches = [cluster for cluster in clusters if re.match(re_pattern, cluster)]
        if len(matches) != 1:
            if len(matches) == 0:
                cls.log_put(LogType.ERROR, f"No cluster names matched regex pattern {re_pattern}")
            else:
                cls.log_put(LogType.ERROR, f"Multiple clusters matched: {matches}")
            cls.set_status(Status.GET_INST, f"Failed to match a cluster")
            return False

        cls.cluster = matches[0]

        cls.set_status(Status.GET_INST, "Cluster sucessfully retrieved")
        return True
        
    # Abstract
    @classmethod
    def is_operational(cls):
        cls.set_status(Status.OPERATIONAL, "Checking")
        status = cls.eks_client.describe_cluster(name=cls.cluster)["cluster"]["status"]
        if status != "ACTIVE":
            cls.log_put(LogType.ERROR, f"Cluster name: {cls.cluster} has status {status}")
            cls.set_status(Status.OPERATIONAL, "Failed: Invalid cluster")
            return False

        cls.set_status(Status.OPERATIONAL, "Valid cluster")
        return True

    # Abstract
    @classmethod
    def get_data(cls):
        cls.set_status(Status.GET_DATA, "Retrieving data")
        cls.data = cls.eks_client.describe_cluster(name=cls.cluster)
        cls.set_status(Status.GET_DATA, "Successful")

        return True

    # Abstract
    @classmethod
    def generate_yaml(cls, yaml):
        cls.yaml_lock.acquire()
        cls.set_status(Status.GENERATE, "Generating yaml")
        target = util.read(cls.config, "eks", "Target")
        if not util.is_present(yaml, *target):
            cls.set_status(Status.GENERATE, "Failed to locate target")
            cls.log_put(LogType.ERROR, "Target {*target} not found in input yaml")
            return False

        yaml = util.write(yaml, cls.cluster, *target)
        cls.set_status(Status.GENERATE, "Successful")
        cls.yaml_lock.release()

        return True

    # Reset before processing next yaml file
    @classmethod
    def reset(cls):
        super().reset()
        cls.eks_client = None
        cls.cluster = None
        cls.data = None

