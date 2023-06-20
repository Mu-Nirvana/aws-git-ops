#!/usr/bin/env python3
from modules import *
import sys
import importlib
from copy import deepcopy
from threading import Lock, Thread

# Check if the files exist
def check_files(files):
    for arg in files:
        if not file_ops.check_file(arg):
            util.error(f"Check path file {arg} does not exist!")

# Load the generator classes and create a shared status object
def load_generators(generator_config):
    generators = {module_name: getattr(importlib.import_module(f"generators.{module_name}"), module_name) for module_name in generator_config.keys()}

    status = {"Status": "Not Started", "isProvisioned": "", "isWired": "", "isValid": "", "getData": "", "generateData": "", "FAILED": False}
    statuses = {generator: status for generator in generators.keys()}

    return generators, statuses

# Configure the generator classes with status object, mutex, config, and yaml and return a list of threads ready to run
def configure_generators(generators, statuses, generator_config, yaml):
    mutex = Lock()
    threads = []

    for generator in generators.values():
        generator.config(generator_config, statuses, mutex)
        threads.append(Thread(target=generator.run, args=(yaml,)))

    return threads

# Main function
def main():
    # Get and check command line arg files
    file_args = sys.argv[1:]
    check_files(file_args)

    # Load yamls
    generator_config = file_ops.get_yaml(file_args[0])
    input_yaml = file_ops.get_yaml(file_args[1]) 
    output_yaml = deepcopy(input_yaml)

    #Load and configure generators
    gens, status = load_generators(generator_config)
    threads = configure_generators(gens, status, generator_config, output_yaml)

    # Start generators
    for thread in threads:
        thread.start()

    #Wait for first generator to finish (testing)
    while threads[0].is_alive():
        print('\033[2K', status, end='\r')
    print(status)

    print(input_yaml)
    print(output_yaml)

if __name__ == "__main__":
    main()
