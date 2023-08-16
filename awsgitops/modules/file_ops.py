import yaml
from os.path import expanduser, exists, abspath
from os import getcwd, remove

#Get a file
def get_file(filename):
    with open(expand_path(filename)) as file:
        return file.read()

#Retrieve yaml from file
def get_yaml(yamlFile):
  with open(expand_path(yamlFile)) as file:
    return yaml.safe_load(file)

#Write a python object to a yaml file
def write_yaml(yamlObj, filename):
    return write_file(filename, yaml.dump(yamlObj))

#Write to a file
def write_file(filename, contents):
    with open(expand_path(filename), 'w') as file:
        return file.write(contents)

#Checkfiles
def check_file(file):
    if not exists(expand_path(file)):
        return False 
    return True

#Expand a relative path, user home path, or path from current directory
def expand_path(path):
    return abspath(expanduser(path))
