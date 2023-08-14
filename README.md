# awsgitops
awsgitops is a tool that automates updating application configuration yaml files with data from AWS infrastructure.
The tool includes a CLI interface and a python package. Yaml files are consumed along with a configuration file that specs target values and sources to be updated. The tool uses generators implemented for each resource type that run in parallel to independently retrieve and update values using [BOTO3](https://boto3.amazonaws.com/).

### Contents
- [Installation and Setup](#installation-and-setup)
- [Configuration](#configuration)
- [Generators](#generators)
- [Use](#Use)

### Notes
- All examples in this documentation are drawn from the [examples](examples)

## Installation and Setup
The tool can be installed either through pip or cloning this repository. pip is recommended as you get both the CLI tool and python package configured out of the box.

### pip install
To install the tool with pip run this in a terminal:
`pip install aws-gitops`

### Cloning
The tool can be installed by cloning this repository:
`git clone https://github.com/Mu-Nirvana/aws-git-ops.git`
Then running the install script:
`python3 setup.py install`

## Configuration
The tool uses BOTO3 to access aws resources so credentials must be configured. Additionally the generators in use must be configured.

### BOTO3
You can configure BOTO3 credentials a variety of ways following the instructions in the [BOTO3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).  You can use any of the methods described except for passing the credentials as parameters.

### Generator config
The generators are configured with a yaml file with this general structure:
```yaml
generatorName:
  name: some_name_regex*
  targets:
  - src: [name]
    targetName:
    - CONFIG_NAME
```
Each generator in use has a dictionary with the same name (available generators and associated name are listed in [generators](#generators)). The dictionary contains the name or identifier for the source resource, and a list of target values. Each element is a dictionary with a source and target. The source is a list of keys and indices that indicate the location of the source value in the BOTO3 response (see the [generators](#generators) section for specifics). The target can either be `targetName` or `targetPath`. `targetName` takes a list of strings that represent the target key to replace the value of. `targetPath` takes a list of list of strings that represent full paths to the value to be changed in the input yaml (the same as the source).  Both of these options take a list to allow the same data to be entered into multiple input yamls with different naming conventions with a single generator configuration, and both can be used together. `targetPath` will be consumed before `targetName` and the provided paths and/or names will be searched in order until the first match is found.

## Generators
### eks
The eks generator class takes a `name` value that is a regex string used to match a cluster name. The generator will stop if there is not a singular match.
The generator then retrieves the associated cluster description for the required values. The response format is documented [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks/client/describe_cluster.html), and any value can be consumed. The `'cluster'` key is implicitly included in the source path.
Here is an example configuration:
```yaml
eks:
  name: eks-stackv.-87ah34
  targets:
  - src: ["name"]
    targetPath: 
    - ["infraConfig", "EKS_CLUSTER"]
  - src: ["endpoint"]
    targetName:
    - ENDPOINT 
```
Input: 
```yaml
RDS_DB_NAME: dev-db01v1-appx-iudi3432
REGION: us-west-2
infraConfig:
  EKS_CLUSTER: eks-stackv1-87ah34
  ENDPOINT: app-dev-wa3v0-redis.897hm.use2.cache.amazon.com
```
Output: 
```yaml
RDS_DB_NAME: dev-db01v1-appx-iudi8753
REGION: us-west-2
infraConfig:
  EKS_CLUSTER: eks-stackv2-87ah34
  ENDPOINT: app-dev-wa3v1-redis.897hm.usw2.cache.amazon.com
```
### rds
The rds generator class takes a `name` value that is a regex string used to match a rds cluster name. The generator will stop if there is not a singular match.
The generator then retrieves the associated cluster description for the required values. The response format is documented [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/describe_db_clusters.html), and any value can be consumed. The cluster dictionary is retrieved automatically by the `DatabaseName` value, thus the source path can begin at that level.
Here is an example configuration:
```yaml
rds:
  name: dev-db01v.-appx-.*
  targets:
  - src: ["DatabaseName"]
    targetPath:
    - [RDS_DB_NAME]
```
Input: 
```yaml
RDS_DB_NAME: dev-db01v1-appx-iudi3432
REGION: us-west-2
infraConfig:
  EKS_CLUSTER: eks-stackv1-87ah34
  ENDPOINT: app-dev-wa3v0-redis.897hm.use2.cache.amazon.com
```
Output: 
```yaml
RDS_DB_NAME: dev-db01v2-appx-iudi8753
REGION: us-west-2
infraConfig:
  EKS_CLUSTER: eks-stackv1-87ah34
  ENDPOINT: app-dev-wa3v0-redis.897hm.use2.cache.amazon.com
```
### Other generators
Generators can be created very easily. The generator classes inherit from a parent spec class. They must implement a `get_instance`, `is_operational`, `get_data`, `generate_yaml`, and `reset` method. The generators are loaded by name from the generators directory (`eks` in the configuration yaml coresponds to `eks.py`).

## Use
### CLI
The CLI has two commands, one for single processing, and one for batch processing. The CLI only supports single input files when using stdout or different output paths due technical limitations with variadic parameters.

#### single
`awsgitops single [OPTIONS] CONFIG INPUT`
Where `CONFIG` is the configuration yaml, and `INPUT` is the input yaml to be modified.
By default the output is not writen to a file, only displayed below the status UI. To ouput to a file use the `--output FILE` option. This will ask for a y/n confirmation that can be overridden with the `--yes` option.
The `--stdout` option will not show the status UI and will only write the ouput file to stdout. Any log warnings or errors will be sent to stderr.

#### batch
`awsgitops batch [OPTIONS] CONFIG [INPUT]...`
Where `CONFIG` is the configuration yaml, and `[INPUT]...` is a list of input yamls.
This command writes the output to the input file. A y/n conifirmation is prompted for every file that can be overridden with the `--yes` option. To check the output without overwriting the input files the `--dryrun` option can be used to print the output without writing.

### Python
The python package can also be used to run the tool, and allows multiple input yamls.
Here is a bare-minimum example:
```python
from awsgitops import awsgitops

config = 'gen_config.yaml'
inputs = ['first.yaml', 'second.yaml']
# Load generators
generator_config, input_yamls, output_yamls = awsgitops.load(config, inputs)
# Run generators
status, log, threads, program_config = awsgitops.start_generators(generator_config, output_yamls)
# Wait for generators to finish
while awsgitops.threads_are_alive(threads):
	pass
# Write the output to 
for i in range(len((inputs)):
  # Only write if the file has been changed
  if input_yamls[i] != output_yamls[i]:
	  awsgitops.write_output(output_yamls[i], inputs[i])
```
- `config` and `inputs` are file names or paths
- `load(config, inputs)` takes the configuration and input yamls and loads the generator config and input yamls as python dictionaries and creates a copy of the inputs to modify
- `start_generators(generator_config, output_yamls)` runs the generators (each in a separate thread) and returns the status object used by the CLI, a shared log list, and the thread objects, and a program config dictionary loaded from the generator config with the optional `config` key (this is currently unused)
- `write_output(yaml, name)` writes the passed dictionary to the given file name or path
