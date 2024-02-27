import sys
import boto3
import argparse
import time
from enum import Enum
from botocore.config import Config
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key,Attr

log_path=sys.path[0]+"/DDB_log_"+str(datetime.now().date())+".json"

def perform_test():

    table_name = 'IoTAppDataTableSimple'
    application_id = 'L;g:QQOoAx&Gg&V'
    region = 'eu-central-1'
    session = boto3.Session(profile_name='admin')
    dynamodb_client = session.client('dynamodb',config=Config(region_name=region))
    end=int(time.time())  # to now
    start=end-6*60*60 # from 6h ago

    f = open(log_path, "a")
    for i in range(1,11):
        query_dynamodb_table(f,i,dynamodb_client,table_name, application_id, str(start), str(end))
    f.close()


def query_dynamodb_table(f,i,client,table_name, application_id, start_time, end_time):

    timer_start = time.time()
    response = client.query(
        TableName=table_name,
        KeyConditionExpression="#appId = :appId AND #time BETWEEN :start AND :end",
        ExpressionAttributeNames={
            "#appId": "applicationId",
            "#time": "time"
        },
        ExpressionAttributeValues={
            ":appId": {"S": application_id},
            ":start": {"N": start_time},
            ":end": {"N": end_time}
        },
        ScanIndexForward=False,
        Limit=100  # Limit to 100 records
    )
    timer_stop = time.time()
    d_time=timer_stop-timer_start
    print("delta_time,"+str(d_time))
    f.write("DDB,"+str(i)+","+str(d_time)+str("\n"))
    #print(response['Items'][0])
    #time.sleep(1)



# Example usage:
if __name__ == "__main__":

    table_name = 'IoTAppDataTableSimple'
    application_id = 'L;g:QQOoAx&Gg&V'
    region = 'eu-central-1'
    session = boto3.Session(profile_name='admin')
    dynamodb_client = session.client('dynamodb',config=Config(region_name=region))

    f = open(log_path, "a")
    for i in range(1,60*5+1):
        end=int(time.time())  # to now
        start=end-6*60*60 # from 6h ago
        query_dynamodb_table(f,i,dynamodb_client,table_name, application_id, str(start), str(end))
        time.sleep(1)
    f.close()

    # items = query_dynamodb_table(0,null,dynamodb_client, table_name, application_id, start_time=str(start), end_time=str(end))

    #print(items)


