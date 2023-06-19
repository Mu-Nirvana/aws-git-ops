from modules import *
import sys

def error(contents):
    print(f"ERROR: {contents}\nExiting program!")
    exit(1)

def main():
    args = sys.argv[1:]
    for arg in args:
        if not file_ops.check_file(arg):
            error(f"Check path file {arg} does not exist!")
    
    generator_config = file_ops.get_yaml(args[0])
    
    input_yamls = [file_ops.get_yaml(file) for file in args[1:]]

    print(generator_config)
    print(input_yamls)
    print(yml.read(generator_config, "CRAZY_FIRST_LEVEL", "LOSING_MY_MIND", 2))
    generator_config = yml.write(generator_config, int(input("Give new number")), "CRAZY_FIRST_LEVEL", "LOSING_MY_MIND", 2)
    print(generator_config)
    if input("Write change?").lower() == "y":
        file_ops.write_yaml(generator_config, args[0])


if __name__ == "__main__":
    main()
