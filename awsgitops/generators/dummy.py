import sys
from .spec import spec
from ..modules import util
from time import sleep

# Example class that doesn't access any AWS instances
class dummy(spec):
    new_data = None
    
    @classmethod
    def is_provisioned(cls):
        cls.set_details("isProvisioned", "Checking") 
        sleep(2)
        cls.set_details("isProvisioned", "Successful")
        return True

    @classmethod
    def is_wired(cls):
        cls.set_details("isWired", "Checking") 
        sleep(2)
        cls.set_details("isWired", "Successful")
        return True

    @classmethod
    def is_valid(cls):
        cls.set_details("isValid", "Checking") 
        sleep(2)
        if input('\033[2K' + "Fail this step? (y/n)\n").lower() == "y":
            cls.set_details("isValid", "Failed")
            return False
        else:
            cls.set_details("isValid", "Successful")
            return True

    @classmethod
    def get_data(cls):
        cls.set_details("getData", "Retrieving data")
        sleep(2)
        cls.new_data = input('\033[2K' + "Input some dummy data to change:\n")
        cls.set_details("getData", "Successful")
        return True

    @classmethod
    def generate_yaml(cls, yaml):
        cls.yaml_lock.acquire()
        cls.set_details("generateData", "Generating yaml")
        sleep(2)
        if not util.is_present(yaml, *util.read(cls.config, "dummy", "TARGET")):
            return False

        yaml = util.write(yaml, cls.new_data, *util.read(cls.config, "dummy", "TARGET"))
        cls.set_details("generateData", "Successful")
        cls.yaml_lock.release()

        return True
