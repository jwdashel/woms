import boto3
import concurrent.futures
import simplejson as json
from typing import List

import pytz
import math
from datetime import datetime

from whatsonms import config
from whatsonms.dynamodb import subdb, metadb

# TIMESTAMP_FMT = "2013-04-11 18:19:07.986"
TIMESTAMP_FMT = "%Y-%m-%d %H:%M:%S.%f"


class Response(dict):
    """
    Simple dictionary class that represents a standard Lambda response
    structure.
    Args:
        status: An integer HTTP status code.
        metadata: A string containing the metadata JSON, default is empty.
        message: A string containing additional info about the response, default
             is empty.
    """

    def __init__(self, status: int, message: str = '', data: dict = {}):
        body = jsonify_body(message, data)
        response = {
            "statusCode": status,
            "headers": {
                "Content-Type": "application/vnd.api+json"
            },
            "body": body,
        }
        dict.__init__(self, **response)


def jsonify_body(message, data):
    """
    Formats the response body to the JSONAPI spec for easy consumption by
    Ember clients.
    """
    metadata = {"meta": {"message": message},
                "data": {
                    "type": "metadata",
                    "id": "1",
                    "attributes": data
                        }
                }
    return json.dumps(metadata)


def convert_time(time_str):
    """
    Convert (david fmt) datetime str to Epoch time.

    Args:
        time_str: Required. Of the format YYYY-MM-DD HH:MM:SS.fff
    Returns: seconds since the Epoch
    """
    track_time = datetime.strptime(time_str, TIMESTAMP_FMT)

    est = pytz.timezone('America/New_York')
    utc = pytz.UTC

    track_time = est.localize(track_time)
    track_time = track_time.astimezone(utc)

    epoch = datetime(1970, 1, 1)
    epoch = utc.localize(epoch)

    epoch_time = math.floor((track_time - epoch).total_seconds())

    return epoch_time


def convert_date_time(date_, time_):
    """
    Convert (nexgen fmt) date str and time str to Epoch time.

    Args:
        date_: Required. Of the format MM/DD/YYYY
        time_: Required. Of the format HH:MM:SS
    Returns: seconds since the Epoch
    """
    month, day, year = date_.split('/')
    date_time = f'{year}-{month}-{day} {time_}.00'
    return convert_time(date_time)


def convert_encoding(win1252str: str) -> str:
    """
    Convert a string encoded with windows-1252 to utf8.

    Args:
        win1252str: Required. A str formatted in windows-1252
    Returns: utf8 string
    """
    encoded_str = win1252str.encode('windows-1252')
    utf_str = encoded_str.decode('utf8')
    return utf_str


def broadcast(stream: str, recipient_ids: List = [],
              data: dict = {}) -> Response:
    """
    Function that manages threaded WebSocket broadcasts to one or more
    connected clients.

    Args:
        stream: Required. A string representing the stream slug.
        recipient_ids: Optional. A list of subscribers connection IDs to send
            to. If none are provided, subscribers for the stream will be fetched
            from the database.
        data: Optional. A json dict representing the message to send. If one
            isn't provided the metadata for the stream will be fetched from the
            database.
    Returns: a Response object.
    """
    ws_client = boto3.Session().client(
        'apigatewaymanagementapi',
        endpoint_url='https://{}/{}'.format(config.WS_DOMAIN, config.WS_STAGE)
    )

    recipient_ids = recipient_ids or subdb.get_subscribers(stream)
    data = data or metadb.get_metadata(stream)
    data_in_bytes = bytes(json.dumps(data), 'utf-8')

    if recipient_ids:
        print('****** RECIPIENT IDS found ******* ', recipient_ids)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_connex_id = {
                executor.submit(_send_message, ws_client, connex_id,
                                data_in_bytes):
                connex_id for connex_id in recipient_ids
            }
            for future in concurrent.futures.as_completed(future_to_connex_id):
                connex_id = future_to_connex_id[future]
            try:
                data = future.result()
            except Exception as e:
                print('{} threw an exception: {}'.format(connex_id, e))

        return Response(200, message="Broadcast sent to %s subscribers" % stream)

    else:
        return Response(200, message="No %s subscribers" % stream)


def _send_message(client, connection_id, data):
    """
    Function that sends a WebSocket message to one subscriber.

    Args:
        client: The initialized WebSocket client
        connection_id: The connection id of the recipient
        data: The message to send, in bytes
    """
    try:
        client.post_to_connection(Data=data, ConnectionId=connection_id)
    except Exception as e:
        for arg in e.args:
            if 'GoneException' in arg:
                # Remove stale connection
                print('*** Subscriber ', connection_id,
                      ' returned response 410: GoneException. Removing subscriber.')
                subdb.unsubscribe(connection_id)
