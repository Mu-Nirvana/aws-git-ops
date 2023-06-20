import sys
sys.path.append('../')
from .generator_spec import generator_spec
from modules import util

class dummy(generator_spec):
    new_data = None

    @classmethod
    def get_data(cls):
        cls.new_data = input("Input some dummy data to change:\n")
        return True

    @classmethod
    def generate_yaml(cls, yaml):
        cls.yaml_lock.acquire()
        if util.read(cls.config, "dummy", "TARGET") not in yaml:
            return False

        yaml = util.write(yaml, cls.new_data, util.read(cls.config, "dummy", "TARGET"))
        cls.yaml_lock.release()

        return True
