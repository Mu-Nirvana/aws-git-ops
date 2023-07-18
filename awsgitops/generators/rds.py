import sys
from ..modules import util
from .genlauncher import Status, LogType
import boto3
import re

class rds():
    rds_client = None
    db = None
    data = None

    # Abstract
    @classmethod
    def get_instance(cls):
        cls.set_status(Status.GET_INST, "Retrieving db")
        cls.rds_client = boto3.client("rds")
        databases = cls.rds_client.describe_db_clusters()["DBClusters"]
        re_pattern = util.read(cls.config, "rds", "Name")

        matches = []
        for database in databases:
            name = database["DatabaseName"]
            if re.match(re_pattern, name):
                matches.append(name)

        if len(matches) != 1:
            if len(matches) == 0:
                cls.log_put(LogType.ERROR, f"No RDS cluster names matched regex pattern {re_pattern}")
            else:
                cls.log_put(LogType.ERROR, f"Multiple RDS clusters matched: {matches}")
            cls.set_status(Status.GET_INST, f"Failed to match a db")
            return False

        cls.db = matches[0]
        
        cls.set_status(Status.GET_INST, "db Successfully retrieved")
        return True
 
    # Abstract
    @classmethod
    def is_operational(cls):
        cls.set_status(Status.OPERATIONAL, "N/A")
        return True

    # Abstract
    @classmethod
    def get_data(cls):
        cls.set_status(Status.GET_DATA, "Retrieving data")
        clusters = cls.rds_client.describe_db_clusters()["DBClusters"]
        for cluster in clusters:
            if cluster["DatabaseName"] == cls.db:
                cls.data = cluster
        
        cls.set_status(Status.GET_DATA, "Successful")
        return True

    # Abstract
    @classmethod
    def generate_yaml(cls, yaml):
        cls.yaml_lock.acquire()
        cls.set_status(Status.GENERATE, "Generating yaml")
        target = util.read(cls.config, "rds", "Target")
        if not util.is_present(yaml, *target):
            cls.set_status(Status.GENERATE, "Failed to locate target")
            cls.log_put(LogType.ERROR, "Target {*target} not found in input yaml")
            return False

        yaml = util.write(yaml, cls.db, *target)
        cls.set_status(Status.GENERATE, "Successful")
        cls.yaml_lock.release()

        return True

    # Reset before processing next yaml file
    @classmethod
    def reset(cls):
        super().reset()
        cls.rds_client = None
        cls.db = None
        cls.data = None

