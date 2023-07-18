from threading import Lock, Thread
from copy import deepcopy
import importlib
from enum import Enum

# Class for the various status categories
class Status(Enum):
     STATUS = 1
     GET_INST = 2
     OPERATIONAL = 3
     GET_DATA = 4
     GENERATE = 5
     FAILED = 6

class LogType(Enum):
    ERROR = 1
    WARNING = 2
    MESSAGE = 3

# Dynamically load generator classes and autopopulate the status dict
def load_generators(generator_config):
    generators = {module_name: getattr(importlib.import_module(f"awsgitops.generators.{module_name}"), module_name) for module_name in generator_config.keys() if module_name != "config"}

    status = {Status.STATUS: "Not Started", Status.GET_INST: "", Status.OPERATIONAL: "", Status.GET_DATA: "", Status.GENERATE: "", Status.FAILED: False}
    statuses = {generator: deepcopy(status) for generator in generators.keys() if generator != "config"}
    log = []

    config = None
    if 'config' in generator_config:
        config = generator_config['config']
    return generators, statuses, log, config 

# Configure the generator classes with status object, mutex, config, and yaml list and return a list of threads ready to run
def configure_generators(generators, statuses, log, generator_config, yamls):
    mutex = Lock()
    threads = []
    
    for generator in generators.values():
        generator.config(generator_config, log, statuses, mutex)
        threads.append(Thread(target=generator.run, args=(yamls,)))

    return threads

