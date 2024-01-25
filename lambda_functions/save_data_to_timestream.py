import json
import boto3
import csv
from decimal import Decimal
import time

def get_data_type(value):
    # Function to determine the data type of the measurement value
    if isinstance(value, int):
        return 'BIGINT'
    elif isinstance(value, float):
        return 'DOUBLE'
    elif isinstance(value, str):
        return 'VARCHAR'
    elif isinstance(value, bool):
        return 'BOOLEAN'
    else:
        return 'UNKNOWN'


def prepare_common_attributes(data):
    # # Extract relevant data from the payload
    applicationId = data.get('applicationId', '')
    domain = data.get('domain', '')
    nodeId = data.get('nodeId', '')

    common_attributes = {
        'Dimensions': [
            {'Name': 'applicationId', 'Value': applicationId},
            {'Name': 'domain', 'Value': domain},
            {'Name': 'nodeId', 'Value': nodeId}
        ],
        'MeasureName': 'all_data',
        'MeasureValueType': 'MULTI'
    }
    return common_attributes



def prepare_record(data):
    # Extract relevant data from the payload
    time = data['time']

    record = {
        "Time":str(time*1000),
        'MeasureValues': []
    }
    return record



def prepare_measure(measure_name, measure_value):

    measure = {
        'Name': str(measure_name),
        'Value': str(measure_value),
        'Type': get_data_type(measure_value)
    }
    return measure

def lambda_handler(event, context):
    try:

        iot_payload=json.loads(json.dumps(event)) #convert data

        # Create a Timestream client
        timestream_client = boto3.client('timestream-write')

        # Specify the Timestream database and table
        database_name = 'IoTAppSimpleTimeStream'
        table_name = 'IoTAppSimpleTimeStreamTable'

        common_attributes=prepare_common_attributes(iot_payload)
        record=prepare_record(iot_payload)

        for measure_name,measure_val in iot_payload["payload"].items():
            record["MeasureValues"].append(prepare_measure(measure_name,measure_val))

        # Write the record to Timestream
        response = timestream_client.write_records(
            DatabaseName=database_name,
            TableName=table_name,
            CommonAttributes=common_attributes,
            Records=[record]
        )

        #print(response)
    except Exception as e:
        print(f"Error writing to Timestream: {e}")
        return {
        'statusCode': 400,
        'body': json.dumps('Data written to Timestream failed!')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Data written to Timestream successfully!')
    }