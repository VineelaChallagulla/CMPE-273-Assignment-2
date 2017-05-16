import boto3
import json


def handler(event, context):
    table = boto3.resource('dynamodb', region_name='us-west-1').Table('menu')
    http_method = event['method']
    if http_method == 'POST':
        table.put_item(Item=event['body'])
        return {}
    elif http_method == 'PUT':
        result = table.update_item(
            Key=event['param'],
            UpdateExpression='SET selection = :selection',
            ExpressionAttributeValues={':selection': event['body']['selection']})
        responseBody = {"menu_id": event['body']['menu_id'],
                    "selection": event['body']['selection']}
        return responseBody
    elif http_method == 'GET':
        return table.get_item(Key=event['param']).get('Item')
    elif http_method == 'DELETE':
        table.delete_item(Key=event['param'])
        return {}
    else:
        raise Exception('Unsupported operation')


