import concurrent.futures
from typing import List
import boto3
from whatsonms import config
import simplejson as json

from whatsonms.dynamodb import subdb, metadb


class Response(dict):
    """
    Args:
        current_track: dict for whats on now (None for no track)
    """

    def __init__(self, current_track, playlist_history, stream, playout_system):
        track = {"data": {
            "id": generate_id(current_track['mm_uid'], current_track['epoch_start_time'], stream),
            "type": "track"
        }} if current_track else {}

        all_tracks = [current_track] + playlist_history
        all_tracks = list(filter(lambda x: x is not None, all_tracks))

        response = {
                "data": {
                    "type": "whats-on",
                    "id": "whats-on",
                    "attributes": {
                        "air-break": not current_track
                    },
                    "meta": {
                        "source": str(playout_system)
                    },
                    "relationships": {
                        "current-track": track,
                        "recent-tracks": {
                            "data": [
                                {"id": generate_id(track['mm_uid'], track['epoch_start_time'], stream), "type": "track"}
                                for track in playlist_history if playlist_history
                            ]
                        }
                    }
                },
                "included": [
                    {"id": generate_id(track['mm_uid'], track['epoch_start_time'], stream), "type": "track",
                     "attributes": track} for track in all_tracks if all_tracks
                ]
        }

        response = Response.dashify_response(response)

        dict.__init__(self, **response)

    def dashify_response(response):
        """
        The front end likes to have dashed-dict-values for their json. Python of
        course likes underscored_dict_values. This goes through and replaces all
        the keys with a dashified version.
        """

        new_response = {}
        for key in response.keys():
            new_key = key.replace('_', '-')
            if type(response[key]) is dict:
                new_response[new_key] = Response.dashify_response(response[key])
            elif type(response[key]) is list:
                new_response[new_key] = [Response.dashify_response(item) if type(item) is dict else item
                                         for item in response[key]]
            else:
                new_response[new_key] = response[key]
        return new_response


class LambdaResponse(dict):
    """
    AWS has specific requirements for how a lambda response is formatted.
    This class accepts a natural response and formats it for use in a lambda.
    """
    def __init__(self, body):
        response = {
            "isBase64Encoded": False,
            "statusCode": 200,
            "multiValueHeaders": {},
            "headers": {
                "Content-Type": "application/vnd.api+json"
            },
            "body": json.dumps(body)
        }
        dict.__init__(self, **response)


class NotFoundResponse(dict):
    def __init__(self):
        response = {"status": 404, "message": "no metadata found"}
        dict.__init__(self, **response)


class ErrorResponse(dict):
    def __init__(self, error_code, error_message):
        response = {"status": error_code, "message": error_message}
        dict.__init__(self, **response)


class BroadcastResponse(dict):
    def __init__(self, message, subscribers, current_track, stream):
        response = {"message": message, "subscribers": subscribers, "current_track": current_track, "stream": stream}
        dict.__init__(self, **response)


class WSResponse(dict):
    def __init__(self, status: int, message: str = '', data: dict = {}):
        response = {
            "statusCode": status,
            "headers": {
                "Content-Type": "application/vnd.api+json"
            },
            "body": data,
        }
        dict.__init__(self, **response)


def generate_id(mm_uid, epoch_start_time, stream):
    return f"{stream}_{epoch_start_time}_{mm_uid}"


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
    data = build_whatson_response(stream)
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

        return BroadcastResponse("Broadcast sent to subscribers", recipient_ids, data, stream)

    else:
        return BroadcastResponse("No subscribers", [], data, stream)


def build_whatson_response(stream):
    metadata = metadb.get_metadata(stream)
    pl_hist = []
    playout_system = metadata.get('playout_system', '')
    if 'playlist_hist_preview' in metadata:
        pl_hist = metadata.get('playlist_hist_preview', [])
        del metadata['playlist_hist_preview']
    return Response(metadata, pl_hist, stream, playout_system)


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
