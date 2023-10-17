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
    #print(config)
    #parameter_names=["applicationId","nodeId","domain"]
    parameter_values=[]
    for param in parameter_names:
        value=config.get(param,"")
        if(value==""):
            print("parameter: "+str(param)+" not exist in config")
        parameter_values.append(value)

    return parameter_values


def get_app_config():
    config_path=sys.path[0]+"/config.json"
    try:
        with open(config_path) as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print("no config.json file in "+str(config_path)+", exiting program ")
        sys.exit(1)

    return config

def get_data():
    return{}

def send_data(data):
    global ipc_client
    global config
    [applicationId,nodeId,domain]=get_app_info(config,parameter_names=["applicationId","nodeId","domain"])
    qos=QOS.AT_LEAST_ONCE
    TIMEOUT=5

    payload_data = dict(payload =data, applicationId = applicationId, nodeId = nodeId,
                        domain = domain, time = int(datetime.now().timestamp()))
    request = PublishToIoTCoreRequest()
    request.topic_name = domain + '/all_data'
    request.payload = bytes(json.dumps(payload_data), "utf-8")
    request.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(request)
    future = operation.get_response()
    future.result(TIMEOUT)
    print("payload_data sent to cloud: "+str(payload_data))

def init_app():
    global ipc_client,config,sending_period
    config={}
    sending_period=30
    config=get_app_config()
    ipc_client=awsiot.greengrasscoreipc.connect()


def main():
    global sending_period
    while(True):
        loop_start_time=time.time()
        data=get_data()
        send_data(data)
        time.sleep(sending_period-(time.time()-loop_start_time))  # starts next loop after sending_period


if(__name__=="__main__"):
    print("iot_app starts")
    init_app()
    main()


