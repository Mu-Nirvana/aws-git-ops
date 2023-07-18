import sys
from ..modules import util
from .spec import spec
from .genlauncher import Status, LogType
import boto3
import re

# Generator class for rds data
class rds(spec):
    rds_client = None
    db = None
    data = None

    # Get the rds cluster
    @classmethod
    def get_instance(cls):
        cls.set_status(Status.GET_INST, "Retrieving db")

        # Get rds clusters
        cls.rds_client = boto3.client("rds")
        databases = cls.rds_client.describe_db_clusters()["DBClusters"]

        # Get name regex pattern
        re_pattern = util.read(cls.config, "rds", "name")

        # Locate name matches
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

        # Save cluster name
        cls.db = matches[0]
        
        cls.set_status(Status.GET_INST, "db Successfully retrieved")
        return True
 
    # Not implemented 
    @classmethod
    def is_operational(cls):
        cls.set_status(Status.OPERATIONAL, "N/A")
        return True

    # Get the entire describe_clusters output for the cluster
    @classmethod
    def get_data(cls):
        cls.set_status(Status.GET_DATA, "Retrieving data")

        # Get the clusters
        clusters = cls.rds_client.describe_db_clusters()["DBClusters"]

        # Find our cluster and save the data
        for cluster in clusters:
            if cluster["DatabaseName"] == cls.db:
                cls.data = cluster
        
        cls.set_status(Status.GET_DATA, "Successful")
        return True

    # Generate yaml
    @classmethod
    def generate_yaml(cls, yaml):
        cls.yaml_lock.acquire()
        cls.set_status(Status.GENERATE, "Generating yaml")

        # Get all data targets
        targets = util.read(cls.config, "rds", "targets")

        for target in targets:
            # Create a list of potential paths to the data
            paths = []
            if 'targetPath' in target:
                paths += target['targetPath']
            if 'targetName' in target:
                for name in target['targetName']:
                    paths += util.find(yaml, name)

            # Check which paths are valid
            valid_paths = [path for path in paths if util.is_present(yaml, *path)]

            if len(paths) == 0 or len(valid_paths) == 0:
                cls.set_status(Status.GENERATE, "Failed to locate target")
                cls.log_put(LogType.ERROR, f"Targets {paths} not found in input yaml")
                return False

            if len(valid_paths) > 1:
                cls.log_put(LogType.WARNING, f"Multiple targets found: {valid_paths}")

            # Read the target data and write it to the valid yaml paths
            src_data = util.read(cls.data, *target["src"])
            for path in valid_paths:
                yaml = util.write(yaml, src_data, *path)

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

