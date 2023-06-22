from threading import Lock, Thread
from copy import deepcopy
import importlib

# Dynamically load generator classes and autopopulate the status dict
def load_generators(generator_config):
    generators = {module_name: getattr(importlib.import_module(f"awsgitops.generators.{module_name}"), module_name) for module_name in generator_config.keys() if module_name != "CONFIG"}

    status = {"Status": "Not Started", "isProvisioned": "", "isWired": "", "isValid": "", "getData": "", "generateData": "", "FAILED": False}
    statuses = {generator: deepcopy(status) for generator in generators.keys() if generator != "CONFIG"}

    return generators, statuses

# Configure the generator classes with status object, mutex, config, and yaml and return a list of threads ready to run
def configure_generators(generators, statuses, generator_config, yaml):
    mutex = Lock()
    threads = []

    for generator in generators.values():
        generator.config(generator_config, statuses, mutex)
        threads.append(Thread(target=generator.run, args=(yaml,)))

    return threads

