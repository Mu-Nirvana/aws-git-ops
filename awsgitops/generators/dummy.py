import sys
from .spec import spec
from ..modules import util
from time import sleep
from .genlauncher import Status, LogType

# Example class that doesn't access any AWS instances
class dummy(spec):
    new_data = None
    
    @classmethod
    def get_instance(cls):
        cls.set_status(Status.GET_INST, "Retrieving")
        sleep(2)
        cls.set_status(Status.GET_INST, "Successful")
        return True

    @classmethod
    def is_operational(cls):
        cls.set_status(Status.OPERATIONAL, "Checking") 
        sleep(2)
        if input("Fail this step? (y/n) ").lower() == "y":
            cls.set_status(Status.OPERATIONAL, "Failed")
            cls.log_put(LogType.ERROR, "Aborted")
            return False
        else:
            cls.set_status(Status.OPERATIONAL, "Successful")
            return True

    @classmethod
    def get_data(cls):
        cls.set_status(Status.GET_DATA, "Retrieving data")
        sleep(2)
        cls.new_data = input('\033[2K' + "Input some dummy data to change:\n")
        cls.set_status(Status.GET_DATA, "Successful")
        return True

    @classmethod
    def generate_yaml(cls, yaml):
        cls.yaml_lock.acquire()
        cls.set_status(Status.GENERATE, "Generating yaml")
        sleep(2)
        if not util.is_present(yaml, *util.read(cls.config, "dummy", "TARGET")):
            return False

        yaml = util.write(yaml, cls.new_data, *util.read(cls.config, "dummy", "TARGET"))
        cls.set_status(Status.GENERATE, "Successful")
        cls.yaml_lock.release()

        return True

    @classmethod
    def reset(cls):
        super().reset()
        new_data = None
