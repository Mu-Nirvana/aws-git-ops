# aws-git-ops

bring your YAML. define your generators. generate your gitops sources.

## Given any input

[sample input file](inputs/dev-env.yml)

## Specify input mapper

[developer specifies generator config for above input](inputs/dev-env-generator-config.yml)


## This tool defines

A class in Go or Python (pseudocode):

- rds.go
```
class rds
    isProvisioned
    isWiredCode // aws cli code or boto-3 code validate rds infra wiring
    isValidCode // aws cli code or boto-3 code validate rds infra validation
    getValueCpde //aws cli code or boto-3 code gets a string value for YAML attribute, e.g., RDS_DB_NAME
    class outputs:
        key  //i.e., RDS_DB_NAME
        type //type is dependent per local path, type example: digitalJulesPipeline
        localPath // windows & mac compatible path string for output file where content is appended
        

```

`Note`: eks.go & redis.go have the same base class as above, but instantiation is different.


## Finally generates

The tool generates new YAML values for each attribute key

[generated output](outputs/dev-env-output.yml)