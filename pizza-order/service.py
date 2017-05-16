from time import gmtime, strftime
import boto3


def handler(event, context):
    order_table = boto3.resource('dynamodb', region_name='us-west-1').Table('order')
    menu_table = boto3.resource('dynamodb', region_name='us-west-1').Table('menu')
    http_method = event['method']
    if http_method == 'POST':
        body = event['body']
        order_table.put_item(Item={
            'menu_id': body['menu_id'],
            'order_id': body['order_id'],
            'customer_name': body['customer_name'],
	    'customer_email': body['customer_email'],
        })
        menu_selection = dict(
            enumerate(menu_table.get_item(Key={'menu_id': body.get('menu_id')}).get('Item').get('selection'), 1))
        response = {
            'message': 'Hi ' + body.get('customer_name') + ', please choose one of these selection:  ' +
                       ', '.join(['{0} {1}'.format(k, v) for k, v in menu_selection.iteritems()])
        }
        return response
    elif http_method == 'PUT':
        body = event['body']
        order_id = event['param']
        menu_id = order_table.get_item(Key=order_id).get('Item').get('menu_id')
        menu_selection = dict(enumerate(menu_table.get_item(Key={'menu_id': menu_id}).get('Item').get('selection'), 1))
        size = dict(enumerate(menu_table.get_item(Key={'menu_id': menu_id}).get('Item').get('size'), 1))
        price = dict(enumerate(menu_table.get_item(Key={'menu_id': menu_id}).get('Item').get('price'), 1))
        user_input = int(event['body'].get('input'))

        if order_table.get_item(Key=order_id).get('Item').get("selection", None) is None:
            if user_input not in menu_selection.keys():
                response = {
                    'message': 'Hi ' + order_table.get_item(Key=order_id).get('Item').get('customer_name') +
                               ', please choose one of these selection:  ' +
                               ', '.join(['{0} {1}'.format(k, v) for k, v in menu_selection.iteritems()])
                }
                raise Exception(response)
            else:
                order_table.update_item(Key=order_id,
                                        UpdateExpression='SET selection = :selection',
                                        ExpressionAttributeValues={':selection': menu_selection.get(user_input)})
                response = {
                    'message': 'Which size do you want? ' + ', '.join(
                        ['{} {}'.format(k, v) for k, v in size.iteritems()])
                }
        elif order_table.get_item(Key=order_id).get('Item').get("size", None) is None:
            if user_input not in size.keys():
                response = {
                    'message': 'Which size do you want? ' + ', '.join(
                        ['{} {}'.format(k, v) for k, v in size.iteritems()])
                }
                raise Exception(response)
            else:
                order_table.update_item(Key=order_id,
                                        UpdateExpression='SET size = :size, price = :price, order_time= :order_time',
                                        ExpressionAttributeValues={
                                            ':size': size.get(user_input),
                                            ':price': str(price.get(user_input)),
                                            ':order_time': strftime("%Y-%m-%d@%H:%M:%S", gmtime())
                                        })
                response = {
                    'message': 'Your order costs ' + price.get(
                        user_input) + '. We will email you when the order is ready. Thank you!'
                }
        else:
            response = {'message': 'Your order is in process. Please wait patiently'}
        return response
    elif http_method == 'GET':
        response = dict()
        order = order_table.get_item(Key=event['param']).get('Item')
        if not order or order.get("order_id", None) is None:
            return  response
        if order.get("selection", None) is None:
            status = "Menu is not selected"
        elif order.get("size", None) is None:
            status = "Size is not selected "
        else:
            status = "Processing"
        response["menu_id"] = order.get("menu_id")
        response["order_id"] = order.get("order_id")
        response["customer_name"] = order.get("customer_name")
        response["customer_email"] = order.get("customer_email")
        response["order_status"] = status
        order_response = dict()
        order_response["selection"] = order.get("selection")
        order_response["size"] = order.get("size")
        order_response["costs"] = order.get("price")
        order_response["order_time"] = order.get("order_time")
        response["order"] = order_response
        return  response

    else:
        raise Exception('Unsupported operation')






