import sys
from ..modules import util
from .spec import spec
from .genlauncher import Status, LogType
import boto3
import re

class rds(spec):
    rds_client = None
    db = None
    data = None

    # Abstract
    @classmethod
    def get_instance(cls):
        cls.set_status(Status.GET_INST, "Retrieving db")

        # Jokes
        #cls.rds_client = boto3.client("rds")
        #databases = cls.rds_client.describe_db_clusters()["DBClusters"]
        databases = [
        {
            'AllocatedStorage': 123,
            'AvailabilityZones': [
                'string',
            ],
            'BackupRetentionPeriod': 123,
            'CharacterSetName': 'string',
            'DatabaseName': 'database_v1',
            'DBClusterIdentifier': 'string',
            'DBClusterParameterGroup': 'string',
            'DBSubnetGroup': 'string',
            'Status': 'string',
            'PercentProgress': 'string',
            'Endpoint': 'string',
            'ReaderEndpoint': 'string',
            'CustomEndpoints': [
                'string',
            ],
            'MultiAZ': True,
            'Engine': 'string',
            'EngineVersion': 'string',
            'Port': 123,
            'MasterUsername': 'string',
            'DBClusterOptionGroupMemberships': [
                {
                    'DBClusterOptionGroupName': 'string',
                    'Status': 'string'
                },
            ],
            'PreferredBackupWindow': 'string',
            'PreferredMaintenanceWindow': 'string',
            'ReplicationSourceIdentifier': 'string',
            'ReadReplicaIdentifiers': [
                'string',
            ],
            'DBClusterMembers': [
                {
                    'DBInstanceIdentifier': 'string',
                    'IsClusterWriter': True,
                    'DBClusterParameterGroupStatus': 'string',
                    'PromotionTier': 123
                },
            ],
            'VpcSecurityGroups': [
                {
                    'VpcSecurityGroupId': 'string',
                    'Status': 'string'
                },
            ],
            'HostedZoneId': 'string',
            'StorageEncrypted': True,
            'KmsKeyId': 'string',
            'DbClusterResourceId': 'string',
            'DBClusterArn': 'string',
            'AssociatedRoles': [
                {
                    'RoleArn': 'string',
                    'Status': 'string',
                    'FeatureName': 'string'
                },
            ],
            'CloneGroupId': 'string',
            'BacktrackWindow': 123,
            'BacktrackConsumedChangeRecords': 123,
            'EnabledCloudwatchLogsExports': [
                'string',
            ],
            'Capacity': 123,
            'EngineMode': 'string',
            'ScalingConfigurationInfo': {
                'MinCapacity': 123,
                'MaxCapacity': 123,
                'AutoPause': True,
                'SecondsUntilAutoPause': 123,
                'TimeoutAction': 'string',
                'SecondsBeforeTimeout': 123
            },
            'DeletionProtection': False,
            'HttpEndpointEnabled': False,
            'ActivityStreamMode': 'sync',
            'ActivityStreamStatus': 'started',
            'ActivityStreamKmsKeyId': 'string',
            'ActivityStreamKinesisStreamName': 'string',
            'CopyTagsToSnapshot': False,
            'CrossAccountClone': False,
            'DomainMemberships': [
                {
                    'Domain': 'string',
                    'Status': 'string',
                    'FQDN': 'string',
                    'IAMRoleName': 'string',
                    'OU': 'string',
                    'AuthSecretArn': 'string',
                    'DnsIps': [
                        'string',
                    ]
                },
            ],
            'TagList': [
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ],
            'GlobalWriteForwardingStatus': 'unknown',
            'GlobalWriteForwardingRequested': False,
            'PendingModifiedValues': {
                'PendingCloudwatchLogsExports': {
                    'LogTypesToEnable': [
                        'string',
                    ],
                    'LogTypesToDisable': [
                        'string',
                    ]
                },
                'DBClusterIdentifier': 'string',
                'MasterUserPassword': 'string',
                'EngineVersion': 'string',
                'BackupRetentionPeriod': 123,
                'AllocatedStorage': 123,
                'Iops': 123,
                'StorageType': 'string'
            },
            'DBClusterInstanceClass': 'string',
            'StorageType': 'string',
            'Iops': 123,
            'MonitoringInterval': 123,
            'MonitoringRoleArn': 'string',
            'PerformanceInsightsKMSKeyId': 'string',
            'PerformanceInsightsRetentionPeriod': 123,
            'ServerlessV2ScalingConfiguration': {
                'MinCapacity': 123.0,
                'MaxCapacity': 123.0
            },
            'NetworkType': 'string',
            'DBSystemId': 'string',
            'MasterUserSecret': {
                'SecretArn': 'string',
                'SecretStatus': 'string',
                'KmsKeyId': 'string'
            },
        },
    ]
        cls.rds_client = databases

        re_pattern = util.read(cls.config, "rds", "name")

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
        # Jokes
        #clusters = cls.rds_client.describe_db_clusters()["DBClusters"]
        clusters = cls.rds_client

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
        targets = util.read(cls.config, "rds", "targets")

        for target in targets:
            paths = []
            if 'targetPath' in target:
                paths += target['targetPath']
            if 'targetName' in target:
                for name in target['targetName']:
                    paths += util.find(yaml, name)
            valid_paths = [path for path in paths if util.is_present(yaml, *path)]

            if len(paths) == 0 or len(valid_paths) == 0:
                cls.set_status(Status.GENERATE, "Failed to locate target")
                cls.log_put(LogType.ERROR, f"Targets {paths} not found in input yaml")
                return False

            if len(valid_paths) > 1:
                cls.log_put(LogType.WARNING, f"Multiple targets found: {valid_paths}")

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

