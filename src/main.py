from modules import *
import sys
from threading import Lock, Thread

# Report an error and exit the program
def error(contents):
    print(f"ERROR: {contents}\nExiting program!")
    exit(1)

# Check if the files exist
def check_files(files):
    for arg in args:
        if not file_ops.check_file(arg):
            error(f"Check path file {arg} does not exist!")

# Load the generator classes and create a shared status object
def load_generators(generator_config):
    generators = {module_name: __import__(f"generators.{module_name}").getattr(module_name) for module_name in generator_config.keys()}

    status = {"Status": "Not Started", "isProvisioned": "", "isWired": "", "isValid": "", "getData": "", "updateData": ""}
    statuses = {generator: status for generator in generators.keys()}

    return generators, statuses

# Configure the generator classes with status object, mutex, config, and yaml and return a list of threads ready to run
def configure_generators(generators, statuses, generator_config, yaml):
    mutex = Lock()
    threads = []

    for generator in generators.values():
        generator.set_status(statuses)
        generator.set_config(generator_config)
        generator.set_mutex(mutex)
        threads.append(target=generator.run, args=(yaml))

    return threads

# Main function
def main():
    # Get and check command line arg files
    file_args = sys.argv[1:]
    check_files(file_args)

    # Load yamls
    generator_config = file_ops.get_yaml(file_args[0])
    input_yaml = file_ops.get_yaml(file_args[1]) 

    #Load and configure generators
    gens, status = load_generators(generator_config)
    threads = configure_generators(gens, status, generator_config, input_yaml)

    # Start generators
    for thread in threads:
        thread.start()

    #Wait for first generator to finish (testing)
    threads[0].join()

if __name__ == "__main__":
    main()
