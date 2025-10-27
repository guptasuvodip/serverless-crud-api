import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('tasks')

def lambda_handler(event, context):
    http_method = event.get('httpMethod')
    
    if http_method == 'GET':
        return handle_get()
    elif http_method == 'POST':
        return handle_post(event, context)
    elif http_method == 'PATCH':
        return handle_patch(event)
    elif http_method == 'DELETE':
        return handle_delete(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid request type',
                'event': event
            })
        }

def handle_get():
    response = table.scan()
    return {
        'statusCode': 200,
        'body': json.dumps(response.get('Items', []))
    }

def handle_post(event, context):
    body = json.loads(event['body'])
    item = {
        'id': context.aws_request_id,
        'name': body['name'],
        'completed': body['completed'],
    }
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Task created successfully'})
    }

def handle_patch(event):
    body = json.loads(event['body'])
    key = {'id': body['id']}
    update_expr = 'SET #n = :name, completed = :completed'
    expr_attr_names = {'#n': 'name'}
    expr_attr_values = {':name': body['name'], ':completed': body['completed']}
    
    response = table.update_item(
        Key=key,
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_values,
        ReturnValues='ALL_NEW'
    )
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Task updated successfully',
            'task': response.get('Attributes')
        })
    }

def handle_delete(event):
    body = json.loads(event['body'])
    key = {'id': body['id']}
    response = table.delete_item(
        Key=key,
        ReturnValues='ALL_OLD'
    )
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Task deleted successfully',
            'task': response.get('Attributes')
        })
    }
