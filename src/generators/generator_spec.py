from ..modules import util

class generator_spec():
    status = None
    confg = None
    yaml_lock = None

    # Abstract
    def is_provisioned():
        return True

    # Abstract
    def is_wired():
        return True
    
    # Abstract
    def is_valid():
        return True

    # Abstract
    def get_data():
        return True

    # Abstract
    def generate_yaml(yaml):
        return True

    # Run all stages of the generator
    def run(yaml):
        if status == None or config == None or yaml_lock == None:
            util.error(f"Generator {__class__.__name__} has not been fully configured")    

        stages = (("Running isProvisioned", is_provisioned, []), ("Running isWired", is_wired, []), ("Running isValid", is_valid, []), ("Running getData", get_data, []), ("Running generateYaml", generate_yaml, [yaml])) 

        set_status("Started")
        
        for stage in stages:
            set_status(stage[0])
            if not stage[1](*stage[2]):
                status["FAILED"] = True
                set_status(f"FAILED")
                return 1

        set_status("FINISHED")
    
    # Set the generators status
    def set_status(status_msg):
        status[__class__.__name__]["Status"] = status_msg

    def config(generator_config, status_object, mutex):
        config = generator_config
        status = status_object
        yaml_lock = mutex
