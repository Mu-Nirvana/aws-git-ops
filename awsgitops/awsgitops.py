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
from .generators.genlauncher import Status, LogType

__version__ = "1.1.0"
DEBUG = False

# Application wide console object 
console = Console()
err_console = Console(stderr=True)

# Color config
class COLORS():
 fail = "#B60324"
 success = "#0D7A95"
 run_check = "#C94E02"
 retrieve_wait = "#FAB372"
 gen = "#8E125E"
 normal = "#FFFFFF"
 warn = "#F58002"


# Style generator status messages
def style(generator_status):
    output = []

    if generator_status[Status.FAILED]:
        for status in list(generator_status.values())[:-1]:
            output.append(f"[{COLORS.fail}]{status}")
        return output
    elif generator_status[Status.STATUS] == "Finished":
        for status in list(generator_status.values())[:-1]:
            output.append(f"[{COLORS.success}]{status}")
        return output

    for stage in [Status.STATUS, Status.GET_INST, Status.OPERATIONAL, Status.GET_DATA, Status.GENERATE]:
        status = generator_status[stage]
        if "successful" in status.lower() or "valid" in status.lower():
            output.append(f"[{COLORS.success}]{status}")
        elif "running" in status.lower() or "started" in status.lower():
            output.append(f"[{COLORS.run_check}]{status}")
        elif "failed" in status.lower():
            output.append(f"[{COLORS.fail}]{status}")
        elif "checking" in status.lower():
            output.append(f"[{COLORS.run_check}]{status}")
        elif "retrieving" in status.lower():
            output.append(f"[{COLORS.retrieve_wait}]{status}")
        elif "generating" in status.lower():
            output.append(f"[{COLORS.gen}]{status}")
        elif "waiting" in status.lower():
            output.append(f"[{COLORS.retrieve_wait}]{status}")
        else:
            output.append(f"[gray70]{status}")

    return output

def format_log(message):
    if message[0] == LogType.ERROR:
        return f"[{COLORS.fail}]ERROR: {message[1]}"
    elif message[0] == LogType.WARNING:
        return f"[{COLORS.warn}]WARNING: {message[1]}"
    elif message[0] == LogType.MESSAGE:
        return f"[{COLORS.normal}]{message[1]}"
    else:
        return f"[gray70]{message[1]}"


# Generate a table view of statuses for the CLI
def generate_status_view(status):
    table = Table(title="[b u]Generator Status", box=box.SIMPLE)

    table.add_column("generator")
    table.add_column("status")
    table.add_column("getInstance")
    table.add_column("isOperational")
    table.add_column("getData")
    table.add_column("generate")

    for generator in status:
        table.add_row(f"[bright_white]{generator}", *style(status[generator]))

    return table


# Load a config and input files as yaml
def load(config, inputs):
    generator_config = file_ops.get_yaml(config)
    input_yamls = [file_ops.get_yaml(input) for input in inputs]
    output_yamls = deepcopy(input_yamls)

    return generator_config, input_yamls, output_yamls


# Configure and start the appropriate generators
def start_generators(config_yaml, output_yamls):
    gens, status, log, config = genlauncher.load_generators(config_yaml)
    threads = genlauncher.configure_generators(gens, status, log, config_yaml, output_yamls)

    for thread in threads:
        thread.start()

    return status, log, threads, config


# Check if any of the threads in the list are still alive
threads_are_alive = lambda threads: any([thread.is_alive() for thread in threads])


# Write yaml to an output file
write_output = lambda output_yaml, output_file: file_ops.write_yaml(output_yaml, output_file)


@click.group()
def main():
    pass

# CLI command (the above methods can be used to implement the same behavior within other applications to allow easy automation)
@click.command()
@click.argument('config', type=click.Path(exists=True))
@click.argument('input', type=click.Path(exists=True))
@click.option('--output', default=None, help="Output file path")
@click.option('--yes', is_flag=True, help="Confirm file write without prompt")
@click.option('--stdout', is_flag=True, help="Write only the output file to stdout to allow output pipes")
def single(config, input, output, yes):
    """Regenrate a single INPUT yaml file"""
    # Load yamls
    generator_config, input_yamls, output_yamls = load(config, [input])

    # Display loaded input
    if not stdout:
        console.print("\n[b u]Input yaml:")
        console.print(yaml.dump(input_yamls[0], default_flow_style=False))

    # Start Generators
    status, log, threads, program_config = start_generators(generator_config, output_yamls)

    #Wait for first generator to finish (testing)
    if not stdout:
        console.print()
        with Live(generate_status_view(status), refresh_per_second=4) as live:
            while threads_are_alive(threads):
                while len(log) > 0:
                    live.console.print(format_log(log.pop(0)))
                live.update(generate_status_view(status))
            while len(log) > 0:
                live.console.print(format_log(log.pop(0)))
            live.update(generate_status_view(status))

    else:
        while threads_are_alive(threads):
            while len(log) > 0:
                message = log.pop(0)
                if message[0] != LogType.MESSAGE:
                    err_console.print(format_log(message))
        while len(log) > 0:
            message = log.pop(0)
            if message[0] != LogType.MESSAGE:
                err_console.print(format_log(message))


    # Display generated yaml
    if not stdout:
        console.print("[b u]Output yaml:")
    console.print(yaml.dump(output_yamls[0], default_flow_style=False))

    # If an output is provided confirm with user and write output
    if output is not None:
        if console.input(f"Would you like to write the output to {output}? ([bright_green]y[/]/[bright_red]n[/])").lower() == "y" or yes:
            write_output(output_yamls[0], output)

@click.command()
@click.argument('config', type=click.Path(exists=True))
@click.argument('input', type=click.Path(exists=True), nargs=-1)
@click.option('--dryrun', is_flag=True, help="Don't write changes to files")
@click.option('--yes', is_flag=True, help="Confirm file write without prompt")
def batch(config, input, dryrun, yes):
    """Regenrate multiple INPUT yaml files and write in place"""
    # Load yamls
    generator_config, input_yamls, output_yamls = load(config, [input])

    # Display loaded input
    console.print("\n[b u]Input yaml:")
    console.print(yaml.dump_all(input_yamls, default_flow_style=False))

    # Start Generators
    status, log, threads, program_config = start_generators(generator_config, output_yamls)

    #Wait for first generator to finish (testing)
    console.print()
    with Live(generate_status_view(status), refresh_per_second=4) as live:
        while threads_are_alive(threads):
            while len(log) > 0:
                live.console.print(format_log(log.pop(0)))
            live.update(generate_status_view(status))
        while len(log) > 0:
            live.console.print(format_log(log.pop(0)))
        live.update(generate_status_view(status))


    # Display generated yaml
    console.print("[b u]Output yaml:")
    console.print(yaml.dump_all(output_yamls, default_flow_style=False))

    # If an output is provided confirm with user and write output
    if not dryrun:
        for x, file in enumerate(input):
            if console.input(f"Would you like to write the output to {file}? ([bright_green]y[/]/[bright_red]n[/])").lower() == "y" or yes:
                write_output(output_yamls[x], file)

main.add_command(single)
main.add_command(batch)
