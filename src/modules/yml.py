def read(yaml, *keys):
    if len(keys) == 1:
        return yaml[keys[0]]
    else:
        return read(yaml[keys[0]], *keys[1:])

def write(yaml, value, *keys):
    if len(keys) == 1:
        yaml[keys[0]] = value
        return yaml
    else:
        yaml[keys[0]] = write(yaml[keys[0]], value, *keys[1:])
        return yaml
