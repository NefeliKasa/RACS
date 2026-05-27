import time
from kubernetes import watch
from utils.logging_config import setup_logger
from k8s_utils.safe_kube_call import safe_kube_call
from k8s_utils.kube_init import custom_obj_api
from controller import RacsController
from constants import GROUP, VERSION, PLURAL

logger = setup_logger(__name__)

def watch_racs_configs():
    w = watch.Watch()
    
    active_controllers = {}

    while True:
        try:
            stream = w.stream(
                custom_obj_api.list_cluster_custom_object,
                GROUP,
                VERSION,
                PLURAL,
                timeout_seconds=300,
            )

            for event in stream:
                racs_config = event["object"]
                event_type = event["type"]
                
                obj_uid = racs_config["metadata"]["uid"]
                obj_name = racs_config["metadata"]["name"]

                if event_type == "ADDED":
                    if obj_uid in active_controllers:
                        logger.info(f"Racs Configuration {obj_name} already exists. Updating state.")
                        active_controllers[obj_uid].patch_racs(racs_config)
                        continue
                    
                    logger.info(f"Racs Configuration {obj_name} added.")
                    
                    controller_instance = RacsController(racs_config)
                    controller_instance.init_racs() 
                    
                    active_controllers[obj_uid] = controller_instance

                elif event_type == "MODIFIED":
                    logger.info(f"Racs Configuration {obj_name} modified.")
                    
                    controller_instance = active_controllers.get(obj_uid)
                    if controller_instance:
                        controller_instance.patch_racs(racs_config)
                    else:
                        logger.warning(f"Received MODIFIED event for unknown Racs Configuration {obj_name}. Ignoring.")

                elif event_type == "DELETED":
                    logger.info(f"Racs Configuration {obj_name} deleted. Cleaning up controller.")
                    
                    controller_instance = active_controllers.pop(obj_uid, None)
                    if controller_instance:
                        controller_instance.delete_racs()
                    else:
                        logger.warning(f"Received DELETED event for unknown Racs Configuration {obj_name}. Ignoring.")
        except Exception as e:
            logger.warning(f"Watcher error or timeout, reconnecting: {e}")
            time.sleep(2)
