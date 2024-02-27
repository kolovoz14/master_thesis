import sys
import boto3
from datetime import datetime
import time
from enum import Enum
from botocore.config import Config


log_path=sys.path[0]+"/Timestream_log_"+str(datetime.now().date())+".json"

def perform_test(client,query_str):
    f = open(log_path, "a")
    for i in range(1,60*5+1):
        single_query(f,i,client,query_str)
        time.sleep(1)
    f.close()


def single_query(f,i,client,query_str):
    #run_query
    start_time = time.time()
    response = client.query(
        QueryString=query_str
    )
    end_time = time.time()
    query_time=end_time-start_time
    f.write("timestream,"+str(i)+","+str(query_time)+str("\n"))


#init boto3
region="eu-central-1"
session = boto3.Session(profile_name='admin')
query_client = session.client('timestream-query', config=Config(region_name=region))

# 100 newest from last 15 min
QUERY_1='SELECT * FROM "IoTAppSimpleTimeStream"."IoTAppSimpleTimeStreamTable" WHERE time between ago(15m) and now() ORDER BY time DESC LIMIT 100'
# 100 newest from last 24 hours
QUERY_2='SELECT * FROM "IoTAppSimpleTimeStream"."IoTAppSimpleTimeStreamTable" WHERE time between ago(24h) and now() ORDER BY time DESC LIMIT 100'
# 100 newest from last 15 min with applicationId
QUERY_3='SELECT * FROM "IoTAppSimpleTimeStream"."IoTAppSimpleTimeStreamTable" WHERE applicationId="iot_app" and time between ago(15m) and now() ORDER BY time DESC LIMIT 10'

# 100 newest from last 6h with applicationId
TEST_QUERY = '''SELECT * FROM "IoTAppSimpleTimeStream"."IoTAppSimpleTimeStreamTable" WHERE applicationId='L;g:QQOoAx&Gg&V' AND time BETWEEN ago(6h) AND now() ORDER BY time DESC LIMIT 100'''


f = open(log_path, "a")
perform_test(query_client,TEST_QUERY)
f.close()
