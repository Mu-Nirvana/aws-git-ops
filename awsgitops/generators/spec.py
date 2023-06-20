import sys
from ..modules import util

class spec():
    status = None
    confg = None
    yaml_lock = None

    # Abstract
    @classmethod
    def is_provisioned(cls):
        return True

    # Abstract
    @classmethod
    def is_wired(cls):
        return True
    
    # Abstract
    @classmethod
    def is_valid(cls):
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

        stages = (("Running isProvisioned", cls.is_provisioned, []), ("Running isWired", cls.is_wired, []), ("Running isValid", cls.is_valid, []), ("Running getData", cls.get_data, []), ("Running generateYaml", cls.generate_yaml, [yaml])) 

        cls.set_status("Started")
        
        for stage in stages:
            cls.set_status(stage[0])
            if not stage[1](*stage[2]):
                cls.status["FAILED"] = True
                cls.set_status(f"FAILED")
                return 1

        cls.set_status("FINISHED")
    
    # Set the generators status
    @classmethod
    def set_status(cls, status_msg):
        cls.status[cls.__name__]["Status"] = status_msg

    @classmethod
    def config(cls, generator_config, status_object, mutex):
        cls.config = generator_config
        cls.status = status_object
        cls.yaml_lock = mutex

    @classmethod
    def set_details(cls, stage, message):
        cls.status[cls.__name__][stage] = message
