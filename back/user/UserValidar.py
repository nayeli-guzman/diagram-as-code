import boto3
import json
import time

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
    }

    try:
        # Extraer token del header Authorization
        auth = event.get('headers', {}).get('Authorization', '')
        if not auth.startswith('Bearer '):
            raise Exception('Missing or invalid Authorization header')
        token = auth.split()[1]

        # También puedes extraer tenant_id de otro header o de context
        tenant_id = event.get('headers', {}).get('x-tenant-id')
        if not tenant_id:
            raise Exception('Missing tenant header')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('ab_tokens_acceso')
        resp = table.get_item(Key={'token': token, 'tenant_id': tenant_id})
        if 'Item' not in resp:
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({'error': 'Unauthorized'})
            }

        if resp['Item']['expires_ts'] < int(time.time()):
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({'error': 'Token expired'})
            }

        # Si es válido, devolvemos la política IAM para permitir la ejecución
        return {
            'principalId': resp['Item']['user_id'],
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Allow',
                        'Resource': event['methodArn']
                    }
                ]
            }
        }

    except Exception as e:
        return {
            'statusCode': 401,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }