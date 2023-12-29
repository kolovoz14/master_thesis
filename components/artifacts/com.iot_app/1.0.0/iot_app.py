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

def get_app_info(config:dict,parameter_names):
    ### reads and returns desired parameters from config variable

    parameter_values=[]
    for param in parameter_names:
        value=config.get(param,"")
        if(value==""):
            print("parameter: "+str(param)+" not exist in config")
        parameter_values.append(value)

    return parameter_values


def get_app_config():
    ### reads config file and return config variable

    config_path=sys.path[0]+"/config.json"
    try:
        with open(config_path) as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print("no config.json file in "+str(config_path)+", exiting program ")
        sys.exit(1)

    return config

def generate_dict_data(keys_number:int=0)->dict:
    ### generate data dictionary with desired size, used to simulate senor data for performance tests

    dict_data={}
    dict_data={i:i for i in range(keys_number)}
    dict_data["data_count"]=keys_number
    return dict_data

def get_data():
    return{}

def send_data(ipc_client,config,data):
    ### sends data to IoT Core

    [applicationId,nodeId,domain]=get_app_info(config,parameter_names=["applicationId","nodeId","domain"])
    qos=QOS.AT_LEAST_ONCE
    TIMEOUT=5

    payload_data = dict(payload =data, applicationId = applicationId, nodeId = nodeId,
                        domain = domain, time = round(datetime.now().timestamp(),3))
    request = PublishToIoTCoreRequest()
    request.topic_name = domain + '/all_data'
    request.payload = bytes(json.dumps(payload_data), "utf-8")
    request.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(request)
    future = operation.get_response()
    future.result(TIMEOUT)
    print("payload_data sent to cloud: "+str(payload_data))

def init_app(sending_period):
    ### initialise app varaibles and objects

    config=get_app_config()
    sending_period=config.get("sending_period",600)
    ipc_client=awsiot.greengrasscoreipc.connect()
    return ipc_client,config,sending_period

def main(ipc_client,config,sending_period):
    ### app main loop

    global test_data
    while(True):
        loop_start_time=time.time()
        send_data(ipc_client,config,data=test_data)
        time.sleep(sending_period-(time.time()-loop_start_time))  # starts next loop after sending_period

def run_test_case(config:dict):
    ### run tests if "tests" parameter in config file exist and is not equal to 0
        test=config.get("tests",0)
        if(test):
            try:
                import test_cases
                test_cases.run_selected_test(test)
                print("finished tests")
            except Exception as e:
                print(e)
            finally:
                return 1
        else:
            return 0

if(__name__=="__main__"):
    print("iot_app starts")
    ipc_client,config,sending_period=init_app(30)
    if(not run_test_case(config)): # if config["tests"]!=0 skip tests and run main app
        test_data={}
        main(ipc_client,config,sending_period)


