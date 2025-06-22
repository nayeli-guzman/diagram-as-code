import boto3
import bcrypt
import json

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json"
}

def lambda_handler(event, context):
    try:
        # Parsea el cuerpo JSON de la petición
        body = json.loads(event.get('body') or '{}')
        user_id   = body.get('user_id')
        tenant_id = body.get('tenant_id')
        password  = body.get('password')

        if not all([user_id, tenant_id, password]):
            return {
                'statusCode': 400,
                'headers': HEADERS,
                'body': json.dumps({
                    'error': 'user_id, tenant_id and password are required'
                })
            }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('ab_usuarios')
        existing = table.get_item(
            Key={'tenant_id': tenant_id, 'user_id': user_id}
        )
        if 'Item' in existing:
            return {
                'statusCode': 400,
                'headers': HEADERS,
                'body': json.dumps({'error': 'User already exists'})
            }

        hashed_pw = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode('utf-8')
        table.put_item(Item={
            'tenant_id': tenant_id,
            'user_id': user_id,
            'password': hashed_pw
        })

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps({
                'message': 'User registered successfully',
                'user_id': user_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps({'error': str(e)})
        }
