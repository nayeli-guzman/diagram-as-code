import boto3
import bcrypt
import uuid
import json
import time
from Utils import load_body

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json"
}

# Caducidad en segundos (5 horas)
EXPIRE_SECONDS = 5 * 3600


def lambda_handler(event, context):
    try:
        body = load_body(event)
        user_id = body.get('user_id')
        tenant_id = body.get('tenant_id')
        password = body.get('password')

        if not all([user_id, tenant_id, password]):
            return {
                'statusCode': 400,
                'headers': HEADERS,
                'body': json.dumps({'error': 'user_id, tenant_id and password are required'})
            }

        dynamodb = boto3.resource('dynamodb')
        table_users = dynamodb.Table('ab_usuarios')
        resp = table_users.get_item(Key={'tenant_id': tenant_id, 'user_id': user_id})
        if 'Item' not in resp:
            return {
                'statusCode': 403,
                'headers': HEADERS,
                'body': json.dumps({'error': 'Invalid credentials'})
            }

        if not bcrypt.checkpw(password.encode(), resp['Item']['password'].encode()):
            return {
                'statusCode': 403,
                'headers': HEADERS,
                'body': json.dumps({'error': 'Invalid credentials'})
            }

        token = str(uuid.uuid4())
        now_ts = int(time.time())
        expires_ts = now_ts + EXPIRE_SECONDS

        table_tokens = dynamodb.Table('ab_tokens_acceso')
        table_tokens.put_item(Item={
            'token': token,
            'tenant_id': tenant_id,
            'user_id': user_id,
            'expires_ts': expires_ts
        })

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps({'token': token, 'expires_ts': expires_ts})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps({'error': str(e)})
        }