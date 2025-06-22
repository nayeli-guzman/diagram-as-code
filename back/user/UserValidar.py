import boto3
from datetime import datetime
import json

table_user = 'usuarios'
table_token = table_user + '-token'

def load_body(event):
    if 'body' not in event:
        return event
    
    if isinstance(event["body"], dict):
        return event['body']
    else:
        return json.loads(event['body'])


def lambda_handler(event, context):

    print(event)

    body = load_body(event)

    token = body.get('token')
    tenant_id = body.get('tenant_id')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_token)
    response = table.get_item(
        Key={
            'token': token,
            "tenant_id": tenant_id
        }
    )
    if 'Item' not in response or response['Item'].get('tenant_id') != tenant_id:
        print("error with ", tenant_id, " response: ", response)
        return {
            'statusCode': 403,
            'body': 'Token no existe'
        }
    else:
        expires = response['Item']['expires']
        print("expires ", expires)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if now > expires:
            return {
                'statusCode': 403,
                'body': 'Token expirado'
            }

    print("success")
    return {
        'statusCode': 200,
        'body': 'Token válido'
    }