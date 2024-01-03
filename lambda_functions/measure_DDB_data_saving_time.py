import json
import time
import boto3
import csv
from decimal import Decimal

def lambda_handler(event, context):

    try:
        #print(event)
        dynamodb = boto3.resource('dynamodb')
        data_table = dynamodb.Table('IoTAppDataTableSimple')

        data=json.loads(json.dumps(event),parse_float=Decimal) #convert data
        start_time = time.time()
        data_table.put_item(Item=data) # save to ddb
        end_time=time.time()

        saving_time = end_time - start_time    # Calculate time difference
        print(f"saving_time: {saving_time} seconds")


        data_count=event["data_count"]
        results_table = dynamodb.Table('DDB_saving_times')
        results_row={'data_count':data_count,'start_time':start_time,'end_time':end_time,'saving_time':saving_time}
        results=json.loads(json.dumps(results_row),parse_float=Decimal) #convert data
        results_table.put_item(Item=results) # save results to ddb


    except Exception as e:
        print(f"Lambda general error: {e}")
        raise e

    return {
            'statusCode': 200,
            'body': json.dumps('Successfully measured and written DDB saving time results')
            }