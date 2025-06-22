import boto3
import json
import time

def lambda_handler(event, context):
    # Leer tenant_id y token desde el body
    body = json.loads(event.get('body') or '{}')
    token = body.get('token')
    tenant_id = body.get('tenant_id')

    if not token or not tenant_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'token and tenant_id are required'})
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ab_tokens_acceso')
    resp = table.get_item(Key={'token': token, 'tenant_id': tenant_id})
    if 'Item' not in resp:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Token no existe'})
        }

    item = resp['Item']
    if item.get('tenant_id') != tenant_id:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Tenant inválido'})
        }

    expires_ts = item['expires_ts']
    now_ts = int(time.time())
    if now_ts > expires_ts:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Token expirado'})
        }

    # Si es válido, retornamos HTTP 200
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Token válido'})
    }
