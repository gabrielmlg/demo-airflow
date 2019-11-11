from __future__ import print_function

import time
from builtins import range
from pprint import pprint
import pandas as pd

import airflow
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

import requests
import json
from datetime import datetime
import numpy as np
import pandas as pd

import boto3
from botocore.exceptions import NoCredentialsError

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2),
}

dag = DAG(
    dag_id='ibovespa',
    default_args=args,
    schedule_interval=None,
)

def parseTimestamp(inputdata):
    timestamplist = []
    timestamplist.extend(inputdata)
    calendertime = []
    
    for ts in timestamplist:
        dt = datetime.fromtimestamp(ts)
        print(dt.date())
        calendertime.append(dt.strftime("%m/%d/%Y"))
        
        #dt.datetime.strptime(date, '"%Y-%m-%d"').date()

    return calendertime

# [START howto_operator_python]
def get_yahoo_finance(ds, **kwargs):
    pprint(kwargs)
    print(ds)
    
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-charts"

    querystring = {"region":"Brasil","lang":"en","symbol":"MGLU3.SA","interval":"1d","range":"max"}

    headers = {
        'x-rapidapi-host': "XXX",
        'x-rapidapi-key': "XXX"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    ibov = json.loads(response.text)
    with open('ibov-MGLU3_max.json', 'w') as json_file:
        json.dump(ibov, json_file)

    meta = ibov['chart']['result'][0]['meta']
    timestamp = ibov['chart']['result'][0]['timestamp']
    indicators = ibov['chart']['result'][0]['indicators']

    date = parseTimestamp(timestamp)
    cot_close = indicators['quote'][0]['close']
    cot_open = indicators['quote'][0]['open']
    cot_low = indicators['quote'][0]['low']
    cot_high = indicators['quote'][0]['high']


    df_stokeHist = pd.DataFrame({'date': date, 
                                'open': cot_open, 
                                'close': cot_close, 
                                'low': cot_low, 
                                'high': cot_high})

    df_stokeHist.to_csv('ibov-MGLU3-max.csv')

ACCESS_KEY = 'XXX'
SECRET_KEY = 'XXX'


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


uploaded = upload_to_aws('ibov-MGLU3_max.json', 'ibov-raw', 'ibov-MGLU3_max.json')

print(uploaded)


run_this = PythonOperator(
    task_id='get_yahoo_finance',
    provide_context=True,
    python_callable=get_yahoo_finance,
    dag=dag,
)
# [END howto_operator_python]

# Generate 5 sleeping tasks, sleeping from 0.0 to 0.4 seconds respectively
task = PythonOperator(
    task_id='upload_to_aws',
    python_callable=upload_to_aws,
    op_kwargs={'local_file': 'ibov-MGLU3_max.json', 
                'bucket': 'ibov-raw', 
                's3_file': 'ibov-MGLU3_max_v2.json'},
    dag=dag,
)

run_this >> task
# [END howto_operator_python_kwargs]