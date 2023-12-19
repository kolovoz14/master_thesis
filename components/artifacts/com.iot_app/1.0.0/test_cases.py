from iot_app import *

print("starts speed_test_cases.py")

def send_different_data_sizes(ipc_client,config,keys_number_list):
    test_data_list=[generate_dict_data(keys_number) for keys_number in keys_number_list]

    for test_data in test_data_list:
        send_data(ipc_client,config,data=test_data)
        time.sleep(1)

def send_one_empty(ipc_client,config):
    send_data(ipc_client,config,data={})

def run_selected_test(test_number=0):
    ipc_client,config,sending_period=init_app(30)
    if(test_number==1):
        send_one_empty(ipc_client,config)
    if(test_number==2):
        keys_number_list=config.get("keys_number_list",[10])
        send_different_data_sizes(ipc_client,config,keys_number_list)