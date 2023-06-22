from .modules import *
import sys
import importlib
import click
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box
from copy import deepcopy
from threading import Lock, Thread
from time import sleep

__version__ = "0.4.2"

DEBUG = False
console = Console()

class COLORS():
 fail = "#B60324"
 success = "#0D7A95"
 run_check = "#C94E02"
 retrieve_wait = "#FAB372"
 gen = "#8E125E"

# Load the generator classes and create a shared status object
def load_generators(generator_config):
    generators = {module_name: getattr(importlib.import_module(f"awsgitops.generators.{module_name}"), module_name) for module_name in generator_config.keys()}

    status = {"Status": "Not Started", "isProvisioned": "", "isWired": "", "isValid": "", "getData": "", "generateData": "", "FAILED": False}
    statuses = {generator: deepcopy(status) for generator in generators.keys()}

    return generators, statuses

# Configure the generator classes with status object, mutex, config, and yaml and return a list of threads ready to run
def configure_generators(generators, statuses, generator_config, yaml):
    mutex = Lock()
    threads = []

    for generator in generators.values():
        generator.config(generator_config, statuses, mutex)
        threads.append(Thread(target=generator.run, args=(yaml,)))

    return threads

def style(generator_status):
    output = []

    if generator_status["FAILED"]:
        for status in list(generator_status.values())[:-1]:
            output.append(f"[{COLORS.fail}]{status}")
        return output
    elif generator_status["Status"] == "Finished":
        for status in list(generator_status.values())[:-1]:
            output.append(f"[{COLORS.success}]{status}")
        return output

    for status in list(generator_status.values())[:-1]:
        if "Successful" in status:
            output.append(f"[{COLORS.success}]{status}")
        elif "Running" in status or "Started" in status:
            output.append(f"[{COLORS.run_check}]{status}")
        elif "Failed" in status or "FAILED" in status:
            output.append(f"[{COLORS.fail}]{status}")
        elif "Checking" in status:
            output.append(f"[{COLORS.run_check}]{status}")
        elif "Retrieving" in status:
            output.append(f"[{COLORS.retrieve_wait}]{status}")
        elif "Generating" in status:
            output.append(f"[{COLORS.gen}]{status}")
        elif "Waiting" in status:
            output.append(f"[{COLORS.retrieve_wait}]{status}")
        else:
            output.append(f"[gray70]{status}")

    return output

def generate_status_view(status):
    table = Table(title="[b u]Generator Status", box=box.SIMPLE)

    table.add_column("Generator")
    for key in list(status[list(status.keys())[0]].keys())[:-1]:
        table.add_column(key)

    for generator in status:
        table.add_row(f"[bright_white]{generator}", *style(status[generator]))

    return table


# Main function
@click.command()
@click.argument('config', type=click.Path(exists=True))
@click.argument('input', type=click.Path(exists=True))
def main(config, input):
    """Regerate the INPUT yaml file with current data specified by CONFIG"""
    # Load yamls
    generator_config = file_ops.get_yaml(config)
    input_yaml = file_ops.get_yaml(input) 
    output_yaml = deepcopy(input_yaml)

    #Load and configure generators
    gens, status = load_generators(generator_config)
    threads = configure_generators(gens, status, generator_config, output_yaml)

    # Start generators
    for thread in threads:
        thread.start()

    #Wait for first generator to finish (testing)
    print()
    with Live(generate_status_view(status), refresh_per_second=4) as live:
        while any([thread.is_alive() for thread in threads]):
            sleep(0.25)
            live.update(generate_status_view(status))
        live.update(generate_status_view(status))

    print()
    print(input_yaml)
    print(output_yaml)
