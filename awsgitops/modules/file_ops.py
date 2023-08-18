from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from os.path import expanduser, exists, abspath
from os import getcwd, remove

class YamlParser(YAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()

PARSER = YamlParser()

#Get a file
def get_file(filename):
    with open(expand_path(filename)) as file:
        return file.read()

#Retrieve yaml from file
def get_yaml(yamlFile):
    return PARSER.load(open(yamlFile))

#Write a python object to a yaml file
def write_yaml(yamlObj, filename):
    return PARSER.dump(yamlObj, open(filename, 'w+'))

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
