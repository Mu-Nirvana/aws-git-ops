from .modules import *
from .generators import genlauncher
import sys
import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box
from copy import deepcopy
from time import sleep

__version__ = "0.4.5"
DEBUG = False

# Application wide console object 
console = Console()

# Color config
class COLORS():
 fail = "#B60324"
 success = "#0D7A95"
 run_check = "#C94E02"
 retrieve_wait = "#FAB372"
 gen = "#8E125E"


# Style generator status messages
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


# Generate a table view of statuses for the CLI
def generate_status_view(status):
    table = Table(title="[b u]Generator Status", box=box.SIMPLE)

    table.add_column("Generator")
    for key in list(status[list(status.keys())[0]].keys())[:-1]:
        table.add_column(key)

    for generator in status:
        table.add_row(f"[bright_white]{generator}", *style(status[generator]))

    return table


# Load a config and input file as yaml
def load(config, input):
    generator_config = file_ops.get_yaml(config)
    input_yaml = file_ops.get_yaml(input) 
    output_yaml = deepcopy(input_yaml)

    return generator_config, input_yaml, output_yaml


# Configure and start the appropriate generators
def start_generators(config_yaml, output_yaml):
    gens, status = genlauncher.load_generators(config_yaml)
    threads = genlauncher.configure_generators(gens, status, config_yaml, output_yaml)

    for thread in threads:
        thread.start()

    return status, threads 


# Check if any of the threads in the list are still alive
threads_are_alive = lambda threads: any([thread.is_alive() for thread in threads])


# Write yaml to an output file
write_output = lambda output_yaml, output_file: file_ops.write_yaml(output_yaml, output_file)


# CLI command (the above methods can be used to implement the same behavior within other applications to allow easy automation)
@click.command()
@click.argument('config', type=click.Path(exists=True))
@click.argument('input', type=click.Path(exists=True))
@click.option('--output', default=None, help="Output file path")
@click.option('--yes', is_flag=True, help="Automatically choose yes for writing file output")
def main(config, input, output, yes):
    """Regerate the INPUT yaml file with current data specified by CONFIG"""
    # Load yamls
    generator_config, input_yaml, output_yaml = load(config, input)

    # Display loaded input
    console.print("\n[b u]Input yaml:")
    console.print(yaml.dump(input_yaml, default_flow_style=False))

    # Start Generators
    status, threads = start_generators(generator_config, output_yaml)

    #Wait for first generator to finish (testing)
    console.print()
    with Live(generate_status_view(status), refresh_per_second=4) as live:
        while threads_are_alive(threads):
            sleep(0.25)
            live.update(generate_status_view(status))
        live.update(generate_status_view(status))

    # Display generated yaml
    console.print("[b u]Output yaml:")
    console.print(yaml.dump(output_yaml, default_flow_style=False))

    # If an output is provided confirm with user and write output
    if output is not None:
        if console.input(f"Would you like to write the output to {output}? ([bright_green]y[/]/[bright_red]n[/])").lower() == "y" or yes:
            write_output(output_yaml, output)
