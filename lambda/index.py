import os
import json
import requests
from requests.auth import HTTPBasicAuth
import boto3

def get_param_value(param_name):
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response['Parameter']['Value']

USERNAME = get_param_value('/wattime/username')
PASSWORD = get_param_value('/wattime/password')
BA = "IE"
THRESHOLD = 20
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

def login(username, password):
    url = 'https://api2.watttime.org/login'
    try:
        rsp = requests.get(url, auth=HTTPBasicAuth(username, password))
    except BaseException as e:
        print(f'There was an error making your login request: {e}')
        return None

    try:
        token = rsp.json()["token"]
    except BaseException:
        print(f'There was an error logging in. The message returned from the api is {rsp.text}')
        return None

    return token

def index(token, ba):
    url = f"https://api2.watttime.org/index?ba={ba}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        rsp = requests.get(url, headers=headers)
    except BaseException as e:
        print(f'There was an error making your index request: {e}')
        return None

    try:
        realtime_index = int(rsp.json()["percent"])
    except BaseException:
        print(f'There was an error getting the index. The message returned from the api is {rsp.text}')
        return None

    return realtime_index

def send_email(message):
    sns = boto3.client("sns")
    sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message)

def handler(event, context):
    token = login(USERNAME, PASSWORD)
    if not token:
        print("You will need to fix your login credentials (username and password at the start of this file) before you can query other endpoints.")
        exit()

    realtime_index = index(token, BA)
    print(realtime_index)

    if realtime_index < THRESHOLD:
        message = "The AWS Batch job has been triggered since the realtime index {realtime_index} is lower than threshold {THRESHOLD}, the batch job has been triggered. This simulates the execution of the batch job."
        send_email(message)
        print(f"Realtime index {realtime_index} is lower than the threshold {THRESHOLD}, the batch job has been triggered.")

    else:
        print(f"Realtime index of {realtime_index} is higher than the threshold {THRESHOLD}, no action taken.")

