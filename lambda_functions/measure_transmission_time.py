import json
import time
import boto3
from decimal import Decimal

def lambda_handler(event, context):
    # Log timestamp upon receiving data from IoT Core topic
    receive_time = time.time()

    try:
        send_time=event["time"]
        data_count=event["data_count"]
        transmission_time = receive_time - send_time    # Calculate time difference
        print(f"transmission_time: {transmission_time} seconds")

        dynamodb = boto3.resource('dynamodb')
        results_table = dynamodb.Table('transmission_times')
        results_row={'data_count':data_count,'send_time':send_time,'receive_time':receive_time,'transmission_time':transmission_time}
        results=json.loads(json.dumps(results_row),parse_float=Decimal) #convert data
        results_table.put_item(Item=results) # save results to ddb

    except Exception as e:
        print(f"Lambda general error: {e}")
        raise e

    return {
            'statusCode': 200,
            'body': json.dumps('Successfully measured and written transmission time results')
            }