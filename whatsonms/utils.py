import boto3
import json
from typing import List

from whatsonms import config
from whatsonms.dynamodb import db


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
    return {"data": {"type": "metadata", "id": "1", "attributes": message}}


def broadcast(stream: str, recipient_ids: List = [],
              data: dict = {}) -> Response:
    """
    """
    ws_client = boto3.Session().client(
        'apigatewaymanagementapi',
        endpoint_url='https://{}/{}'.format(config.WS_DOMAIN, config.WS_STAGE)
    )

    recipient_ids = recipient_ids or db.get_subscribers(stream)
    data = data or db.get_metadata(stream)
    data_bytes = bytes(json.dumps(data), 'utf-8')

    # TODO: make this async:
    for recipient_id in recipient_ids:
        ws_client.post_to_connection(
            Data=data_bytes, ConnectionId=recipient_id
        )
    return Response(200, message='message sent')
