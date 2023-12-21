import json
import time
#import boto3


def lambda_handler(event, context):
    # Log timestamp upon receiving data from IoT Core topic
    receive_time = time.time()

    try:
        send_time=event["time"]
        transmission_time = receive_time - send_time    # Calculate time difference
        print(f"transmission_time: {transmission_time} seconds")

    except Exception as e:
        print(f"Error calculating transmission time: {e}")
        raise e

    return {
            'statusCode': 200,
            'body': json.dumps('Calculating transmission time sucessfull')
            }