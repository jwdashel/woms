import boto3
import concurrent.futures
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
    data_in_bytes = bytes(json.dumps(data), 'utf-8')

    # TODO: make this async:
    # for recipient_id in recipient_ids:
    #     ws_client.post_to_connection(
    #         Data=data_in_bytes, ConnectionId=recipient_id
    #     )

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_connex_id = {
            executor.submit(_send_message, ws_client, connex_id, data_in_bytes):
            connex_id for connex_id in recipient_ids
        }
        for future in concurrent.futures.as_completed(future_to_connex_id):
            connex_id = future_to_connex_id[future]
        try:
            data = future.result()
        except Exception as e:
            print('{} threw an exception: {}'.format(connex_id, e))

    return Response(200, message='message sent')


def _send_message(client, connection_id, data):
    client.post_to_connection(Data=data_in_bytes, ConnectionId=recipient_id)
