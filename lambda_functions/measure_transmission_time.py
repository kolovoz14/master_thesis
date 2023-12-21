import json
import time
import boto3
import csv

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
        #fieldnames = ['data_count','send_time', 'receive_time', 'transmission_time']
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
    # Log timestamp upon receiving data from IoT Core topic
    receive_time = time.time()

    try:
        send_time=event["time"]
        data_count=event["data_count"]

        transmission_time = receive_time - send_time    # Calculate time difference
        print(f"transmission_time: {transmission_time} seconds")

        s3 = boto3.client('s3')
        bucket_name = 'iot-performance-tests'
        s3_key = 'transmission_time_results.csv'
        is_file_exists=check_if_file_exists(s3,bucket_name,s3_key)

        file_name = '/tmp/transmission_time_results.csv'
        data_row={'data_count':data_count,'send_time':send_time,'receive_time':receive_time,'transmission_time':transmission_time}
        write_results_to_file(s3,bucket_name,s3_key,file_name,is_file_exists,data_row)


    except Exception as e:
        print(f"Lambda general error: {e}")
        raise e

    return {
            'statusCode': 200,
            'body': json.dumps('Successfully measured and written transmission time results')
            }