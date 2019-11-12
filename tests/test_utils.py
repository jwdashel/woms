import simplejson as json
from unittest.mock import patch
import whatsonms.utils as utils


class TestUtils:
    def test_broadcast(self):
        response = utils.broadcast('wqxr', [], {})
        body = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert body['meta']['message'] == 'No wqxr subscribers'

    def test_broadcast_with_subscribers(self):
        response = utils.broadcast('wqxr', [123, 456, 789], {})
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['meta']['message'] == 'Broadcast sent to wqxr subscribers'

    # [jd 11/6/19] NOTE: moto3 does not currently support mocking
    #                    APIGatewayManagementAPI so I gotta do it
    #                    manually with these patches.
    @patch('whatsonms.utils.boto3')
    def test_broadcast_notifies_ws_connections(self, boto):
        conn_id = 7779311
        data = {'meta': 'data'}
        response = utils.broadcast('wqxr', [conn_id], data)
        assert response['statusCode'] == 200
        boto.Session().client().post_to_connection.assert_called()
        boto.Session().client().post_to_connection.assert_called_with(
                Data=bytes(json.dumps(data), 'utf-8'),
                ConnectionId=conn_id)

    @patch('whatsonms.utils.subdb')
    @patch('whatsonms.utils.boto3')
    def test_removes_stale_subscriber(self, boto, subscriptiondb):
        def side_effect(Data="", ConnectionId=""): raise Exception("GoneException")
        boto.Session().client().post_to_connection.side_effect = side_effect
        conn_id = 7779311
        data = {'meta': 'data'}
        response = utils.broadcast('wqxr', [conn_id], data)
        assert response['statusCode'] == 200
        subscriptiondb.unsubscribe.assert_called_with(conn_id)

    def test_convert_datetime(self):
        current_date = "2019-11-08 12:29:42.986"
        epoch_time = 1573234182
        assert epoch_time == utils.convert_time(current_date)

    def test_convert_date_and_time(self):
        current_date = "11/12/2018"
        current_time = "12:22:19"
        epoch_time = 1542043339
        assert epoch_time == utils.convert_date_time(current_date, current_time)
