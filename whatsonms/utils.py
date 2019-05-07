import boto3
import json
from typing import List


class Response(dict):
    """
    Simple dictionary class that represents a standard Lambda response
    structure.
    Args:
        status: An integer HTTP status code.
        message: A string containing the metadata JSON, default is empty.
    """
    def __init__(self, status: int, message: str = ''):
        if message:
            message = jsonify_message(message)
        response = {
            "statusCode": status,
            "headers": {
                "Content-Type": "application/vnd.api+json"
            },
            "body": message,
        }
        dict.__init__(self, **response)


def jsonify_message(message):
    return json.dumps(
        {"data": {"type": "metadata", "id": "1", "attributes": message}}
    )


def broadcast(event: dict, recipient_ids: List = [], data: str = '',
              stream: str = '') -> Response:
    # TODO: figure out how to build enpoint_url for the case
    # when this fx is called by a http.py method. i.e.
    # is domainName always t5xpql2hqf.execute-api.us-east-1.amazonaws.com ?
    ws_client = boto3.Session().client(
        'apigatewaymanagementapi',
        endpoint_url='https://{}/{}'.format(
            # Does domainName always stay the same for all websocket requests?
            event['requestContext']['domainName'],
            event['requestContext']['stage']
        )
    )

    # TODO: make this async:
    for recipient_id in recipient_ids:
        ws_client.post_to_connection(
            Data=bytes(data, 'utf-8'), ConnectionId=recipient_id
        )
    return Response(200, message='message sent')
