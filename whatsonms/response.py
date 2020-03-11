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
        track = { "data": {
            "id": generate_id(current_track, stream),
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
                    "track": track,
                    "recent-tracks": {
                        "data": [
                            { "id": generate_id(track, stream), "type": "track" } for track in playlist_history if playlist_history
                        ]
                    }
                }
            },
            "included": [
                { "id": generate_id(track, stream), "type": "track", 
                  "attributes": track} for track in all_tracks if all_tracks
            ]
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
        response = { "message": message, "subscribers": subscribers, "current_track": current_track, "stream": stream }
        dict.__init__(self, **response)

def generate_id(track, stream):
    return f"{stream}_{track['epoch_start_time']}_{track['mm_uid']}"


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

        return BroadcastResponse("Broadcast sent to subscribers", recipient_ids, data, stream)

    else:
        return BroadcastResponse("No subscribers", [], data, stream)


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
