import sys
from .spec import spec
from ..modules import util
from time import sleep
from awsgitops.awsgitops import DEBUG
from .genlauncher import Status

# Second example class
class dummytwo(spec):
    new_data = None
    
    @classmethod
    def get_instance(cls):
        cls.set_status(Status.GET_INST, "Checking") 
        sleep(3)
        cls.set_status(Status.GET_INST, "Successful")
        return True

    @classmethod
    def is_operational(cls):
        cls.set_status(Status.OPERATIONAL, "Checking") 
        sleep(1)
        if DEBUG:
            cls.set_status(Status.OPERATIONAL, "Failed")
            return False
        cls.set_status(Status.OPERATIONAL, "Successful")
        return True

    @classmethod
    def get_data(cls):
        cls.set_status(Status.GET_DATA, "Retrieving data")
        sleep(2)
        cls.new_data = "blah blah" 
        cls.set_status(Status.GET_DATA, "Successful")
        return True

    @classmethod
    def generate_yaml(cls, yaml):
        cls.yaml_lock.acquire()
        cls.set_status(Status.GENERATE, "Generating yaml")
        sleep(5)
        if not util.is_present(yaml, *util.read(cls.config, "dummytwo", "TARGET")):
            return False

        yaml = util.write(yaml, cls.new_data, *util.read(cls.config, "dummytwo", "TARGET"))
        cls.set_status(Status.GENERATE, "Successful")
        cls.yaml_lock.release()

        return True
