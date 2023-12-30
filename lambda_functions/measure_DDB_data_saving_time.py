import json
import time
import boto3
import csv
from decimal import Decimal

def check_if_file_exists(s3_client:boto3.client,bucket_name,s3_key):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        # If the file exists, proceed to append data
        is_file_exists = True
    except Exception as e:
        # If the file doesn't exist, set the flag to write headers
        is_file_exists = False
    return is_file_exists

def write_results_to_file(s3_client:boto3.client,bucket_name,s3_key,file_name,is_file_exists,data_row):

    # If the file doesn't exist, write headers and data
    with open(file_name, mode='a', newline='') as csv_file:
        #fieldnames = ['data_count','start_time', 'end_time', 'saving_time']
        field_names=list(data_row.keys())
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        if not is_file_exists: # If the file doesn't exist, write headers
            writer.writeheader()
        writer.writerow(data_row)

    # Upload the updated CSV file to S3
    s3_client.upload_file(file_name, bucket_name, s3_key)

    return {
        'statusCode': 200,
        'body': 'CSV file updated'
    }


def lambda_handler(event, context):

    try:
        print(event)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('IoTAppDataTableSimple')

        data=json.loads(json.dumps(event),parse_float=Decimal) #convert data
        start_time = time.time()
        table.put_item(Item=data) # save to ddb
        end_time=time.time()

        saving_time = end_time - start_time    # Calculate time difference
        print(f"saving_time: {saving_time} seconds")

        s3 = boto3.client('s3')
        data_count=event["data_count"]
        bucket_name = 'iot-performance-tests'
        s3_key = 'DDB_saving_time_results.csv'
        is_file_exists=check_if_file_exists(s3,bucket_name,s3_key)

        file_name = '/tmp/DDB_saving_time_results.csv'
        data_row={'data_count':data_count,'saving_start_time':start_time,'saving_end_time':end_time,'saving_time':saving_time}
        write_results_to_file(s3,bucket_name,s3_key,file_name,is_file_exists,data_row)


    except Exception as e:
        print(f"Lambda general error: {e}")
        raise e

    return {
            'statusCode': 200,
            'body': json.dumps('Successfully measured and written DDB saving time results')
            }