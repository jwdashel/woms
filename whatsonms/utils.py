import boto3
import json
from typing import List

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
    return json.dumps(
        {"data": {"type": "metadata", "id": "1", "attributes": message}}
    )


def broadcast(event: dict, stream: str, recipient_ids: List = [],
              data: dict = {}) -> Response:
    # TODO:
    # 1. get WS domainName from an environment variable, not the event obj, bc
    #    http events have a different domainName than WS events.
    #    WS demo domainName is: t5xpql2hqf.execute-api.us-east-1.amazonaws.com
    #
    # 2. figure out how to allow lambda-whats-on access to post to WS connection.
    #    See error: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group=/aws/lambda/whats-on-demo;stream=2019/05/08/%5B$LATEST%5D3b75698cf7d64f84b9802456cd91fa78;refid=34729721423684293438146518589248016774549751497988046850;reftime=1557334569518

    ws_client = boto3.Session().client(
        'apigatewaymanagementapi',
        endpoint_url='https://{}/{}'.format(
            event['requestContext']['domainName'],
            event['requestContext']['stage']
        )
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
