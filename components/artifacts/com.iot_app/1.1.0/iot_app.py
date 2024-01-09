import json
import time
from threading import Timer
import time
import os
import sys
from datetime import datetime
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToIoTCoreRequest,
)

import shadow_module_v3 as shad_mod
import logging


def configure_logger():
    logFormatter = logging.Formatter("%(message)s") # other info are build in default greengrass logger

    # mian program logger
    logger = logging.getLogger(__name__)
    stream_handler=logging.StreamHandler()
    stream_handler.setFormatter(logFormatter)
    logger.addHandler(stream_handler)  # writing to console
    logger.setLevel(logging.INFO)

    # shadow logger
    shadow_logger = logging.getLogger('shadow_module_v3')
    shadow_logger.addHandler(stream_handler)  # writing to console
    shadow_logger.setLevel(logging.WARNING)

    return logger


def get_app_info(config:dict,parameter_names):
    ### reads and returns desired parameters from config variable

    parameter_values=[]
    for param in parameter_names:
        value=config.get(param,"")
        if(value==""):
            logger.info("parameter: "+str(param)+" not exist in config")
        parameter_values.append(value)

    return parameter_values


def get_app_config():
    ### reads config file and return config variable

    config_path=sys.path[0]+"/config.json"
    try:
        with open(config_path) as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        logger.info("no config.json file in "+str(config_path)+", exiting program ")
        sys.exit(1)

    return config

def get_data():
    # This is a template function change it to read data from sensors or other devices
    return{}

def send_data(ipc_client,config,data):
    ### sends data to IoT Core

    [applicationId,nodeId,domain]=get_app_info(config,parameter_names=["applicationId","nodeId","domain"])
    qos=QOS.AT_LEAST_ONCE
    TIMEOUT=5

    payload_data = dict(payload =data, applicationId = applicationId, nodeId = nodeId,
                        domain = domain, time = round(datetime.now().timestamp(),3))
    if(config.get("tests",0)!=0):
        payload_data["data_count"]=len(payload_data["payload"])
    request = PublishToIoTCoreRequest()
    request.topic_name = domain + '/all_data'
    request.payload = bytes(json.dumps(payload_data), "utf-8")
    request.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(request)
    future = operation.get_response()
    future.result(TIMEOUT)
    logger.info("payload_data sent to cloud: "+str(payload_data))


def init_aws_connection(config_name):
    ### connect to iot core,get thing name, get config from shadow,start subscribing to shadow delta
    try:
        ipc_client=awsiot.greengrasscoreipc.connect()
        thing_name=sys.argv[1]
        config=shad_mod.get_device_shadow_config(ipc_client=ipc_client,thing_name=thing_name,shadow_config_name=config_name)
        shadow_config_sub_handler=shad_mod.subscribe_to_config_delta(ipc_client=ipc_client,thing_name=thing_name,shadow_config_name=config_name)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    return ipc_client,config,shadow_config_sub_handler,thing_name

def main():
    ### app main loop
    shadow_config_name="iot_app_config"  # unique for application type
    ipc_client,config,shadow_config_sub_handler,thing_name=init_aws_connection(shadow_config_name)
    sending_period=config.get("sending_period",600)

    if(run_test_case(ipc_client,config)): # if config["tests"]!=0 skip tests and run main app, else run tests and exit
       sys.exit(1)

    while(True):
        loop_start_time=time.time()
        sample_data=get_data()
        send_data(ipc_client,config,data=sample_data)

        # Update config if received any updates from device shadow
        if(len(shadow_config_sub_handler.message_queue)>0): # new delta message, update config
            config=shad_mod.update_shadow_with_delta(ipc_client,config,thing_name,shadow_config_name,shadow_config_sub_handler)
            sending_period=config.get("sending_period",600)

        time.sleep(sending_period-(time.time()-loop_start_time))  # starts next loop after sending_period

def run_test_case(ipc_client,config:dict):
    ### run tests if "tests" parameter in config file exist and is not equal to 0
        test=config.get("tests",0)
        if(test):
            try:
                import test_cases
                test_cases.run_selected_test(ipc_client,config)
                logger.info("finished tests")
            except Exception as e:
                logger.info(e)
            finally:
                return 1
        else:
            return 0

if(__name__=="__main__"):
    logger=configure_logger()
    logger.info("iot_app starts")
    main()


