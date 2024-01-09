from iot_app import *

print("starts speed_test_cases.py")

def generate_dict_data(keys_number:int=0)->dict:
    ### generate data dictionary with desired size, used to simulate senor data for performance tests

    dict_data={}
    dict_data={i:i for i in range(keys_number)}
    return dict_data

def send_different_data_sizes(ipc_client,config,keys_number_list):
    test_data_list=[generate_dict_data(keys_number) for keys_number in keys_number_list]

    for test_data in test_data_list:
        for i in range(10):
            send_data(ipc_client,config,data=test_data)
            time.sleep(1)

def send_one_empty(ipc_client,config):
    send_data(ipc_client,config,data={})

def run_selected_test(ipc_client,config,test_number=0):
    print(f"starting test case {test_number}")
    if(test_number==1):
        send_one_empty(ipc_client,config)
    if(test_number==2):
        keys_number_list=config.get("keys_number_list",[10])
        send_different_data_sizes(ipc_client,config,keys_number_list)