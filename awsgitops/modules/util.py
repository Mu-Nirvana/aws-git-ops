# Report an error and exit the program
def error(contents):
    print(f"ERROR: {contents}\nExiting program!")
    exit(1)

# Read a value from a yaml object with a variable number of keys
def read(yaml, *keys):
    if len(keys) == 1:
        return yaml[keys[0]]
    else:
        return read(yaml[keys[0]], *keys[1:])

# Check if a key is present in a yaml object
def is_present(yaml, *keys):
    if len(keys) == 1:
        if keys[0] in yaml: return True
        return False
    else:
        if keys[0] not in yaml: return False
        return read(yaml[keys[0]], *keys[1:])

# Find the path to a key in a yaml object
def find(yaml, key, path=[]):
    matches = []
    if type(yaml) != dict and type(yaml) != list:
        return matches 
    for x, item in enumerate(yaml):
        if item == key:
            matches.append(path + [key])
            return matches 
        if type(yaml) == dict:
            result = find(yaml[item], key, path=path+[item])
        else:
            result = find(yaml[x], key, path=path+[x])
        matches += result
    return matches

# Write a value to a yaml object with a variable number of keys
def write(yaml, value, *keys):
    if len(keys) == 1:
        yaml[keys[0]] = value
        return yaml
    else:
        yaml[keys[0]] = write(yaml[keys[0]], value, *keys[1:])
        return yaml
