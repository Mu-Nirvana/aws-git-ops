import sys
from ..modules import util
from .spec import spec
from .genlauncher import Status, LogType
import boto3
import re

class eks(spec):
    eks_client = None
    cluster = None
    data = None

    # Abstract
    @classmethod
    def get_instance(cls):
        cls.set_status(Status.GET_INST, "Retrieving cluster")

        # Jokes
        # cls.eks_client = boto3.client('eks')
        # clusters = cls.eks_client.list_clusters()["clusters"]

        clusters = ['devel', 'prod', 'eks_cluster_v2']

        re_pattern = util.read(cls.config, "eks", "name")
        
        matches = [cluster for cluster in clusters if re.match(re_pattern, cluster)]
        if len(matches) != 1:
            if len(matches) == 0:
                cls.log_put(LogType.ERROR, f"No cluster names matched regex pattern {re_pattern}")
            else:
                cls.log_put(LogType.ERROR, f"Multiple clusters matched: {matches}")
            cls.set_status(Status.GET_INST, f"Failed to match a cluster")
            return False

        cls.cluster = matches[0]

        cls.set_status(Status.GET_INST, "Cluster successfully retrieved")
        return True
        
    # Abstract
    @classmethod
    def is_operational(cls):
        cls.set_status(Status.OPERATIONAL, "Checking")

        # Jokes
        #status = cls.eks_client.describe_cluster(name=cls.cluster)["cluster"]["status"]
        status = "ACTIVE"

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

        # Jokes
        #cls.data = cls.eks_client.describe_cluster(name=cls.cluster)
        cls.data = \
{
    'cluster': {
        'name': 'eks_cluster_v1',
        'arn': 'string',
        'version': 'string',
        'endpoint': 'somewhere over yonder',
        'roleArn': 'string',
        'resourcesVpcConfig': {
            'subnetIds': [
                'string',
            ],
            'securityGroupIds': [
                'string',
            ],
            'clusterSecurityGroupId': 'string',
            'vpcId': 'string',
            'publicAccessCidrs': [
                'string',
            ]
        },
        'kubernetesNetworkConfig': {
            'serviceIpv4Cidr': 'string',
            'serviceIpv6Cidr': 'string',
            'ipFamily': 'ipv6'
        },
        'logging': {
            'clusterLogging': [
                {
                    'types': [
                        'api',
                    ],
                    'enabled': True
                },
            ]
        },
        'identity': {
            'oidc': {
                'issuer': 'string'
            }
        },
        'status': 'ACTIVE',
        'certificateAuthority': {
            'data': 'string'
        },
        'clientRequestToken': 'string',
        'platformVersion': 'string',
        'tags': {
            'string': 'string'
        },
        'encryptionConfig': [
            {
                'resources': [
                    'string',
                ],
                'provider': {
                    'keyArn': 'string'
                }
            },
        ],
        'connectorConfig': {
            'activationId': 'string',
            'activationCode': 'string',
            'provider': 'string',
            'roleArn': 'string'
        },
        'id': 'string',
        'health': {
            'issues': [
                {
                    'code': 'AccessDenied',
                    'message': 'string',
                    'resourceIds': [
                        'string',
                    ]
                },
            ]
        },
        'outpostConfig': {
            'outpostArns': [
                'string',
            ],
            'controlPlaneInstanceType': 'string',
            'controlPlanePlacement': {
                'groupName': 'string'
            }
        }
    }
}
        cls.set_status(Status.GET_DATA, "Successful")

        return True

    # Abstract
    @classmethod
    def generate_yaml(cls, yaml):
        cls.yaml_lock.acquire()
        cls.set_status(Status.GENERATE, "Generating yaml")
        targets = util.read(cls.config, "eks", "targets")

        for target in targets:
            paths = []
            if 'targetPath' in target:
                paths += target['targetPath']
            if 'targetName' in target:
                for name in target['targetName']:
                    paths += util.find(yaml, name)

            if 'targetPath' not in target and 'targetName' not in target:
                cls.set_status(Status.GENERATE, "Failed to locate target")
                cls.log_put(LogType.ERROR, f"No targets provided in generator config")
                return False

            valid_paths = [path for path in paths if util.is_present(yaml, *path)]

            if len(valid_paths) == 0:
                cls.set_status(Status.GENERATE, "Failed to locate target")
                if len(paths) == 0:
                    cls.log_put(LogType.ERROR, f"No targets with names {target['targetName']} found in input yaml")
                else:
                    cls.log_put(LogType.ERROR, f"Targets {paths} not found in input yaml")

                return False

            if len(valid_paths) > 1:
                cls.log_put(LogType.WARNING, f"Multiple targets found: {valid_paths}")

            src_data = util.read(cls.data, "cluster", *target["src"])
            for path in valid_paths:
                yaml = util.write(yaml, src_data, *path)

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

