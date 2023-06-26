import sys
from ..modules import util
from .genlauncher import Status

class spec():
    status = None
    confg = None
    yaml_lock = None

    # Abstract
    @classmethod
    def get_instance(cls):
        return True
 
    # Abstract
    @classmethod
    def is_operational(cls):
        return True

    # Abstract
    @classmethod
    def get_data(cls):
        return True

    # Abstract
    @classmethod
    def generate_yaml(cls, yaml):
        return True

    # Run all stages of the generator
    @classmethod
    def run(cls, yaml):
        if cls.status == None or cls.config == None or cls.yaml_lock == None:
            util.error(f"Generator {__class__.__name__} has not been fully configured")    

        stages = (("Running getInstance", cls.get_instance, []), ("Running isOperational", cls.is_operational, []), ("Running getData", cls.get_data, []), ("Running generateYaml", cls.generate_yaml, [yaml])) 

        cls.set_status(Status.STATUS, "Started")
        for status in [Status.GET_INST, Status.OPERATIONAL, Status.GET_DATA, Status.GENERATE]:
            cls.set_status(status, "Waiting")
        
        for stage in stages:
            cls.set_status(Status.STATUS, stage[0])
            if not stage[1](*stage[2]):
                cls.set_status(Status.FAILED, True)
                cls.set_status(Status.STATUS, "FAILED")
                return 1

        cls.set_status(Status.STATUS, "Finished")
    
    # Set the generators status
    @classmethod
    def set_status(cls, status, status_msg):
        cls.status[cls.__name__][status] = status_msg

    @classmethod
    def config(cls, generator_config, status_object, mutex):
        cls.config = generator_config
        cls.status = status_object
        cls.yaml_lock = mutex
