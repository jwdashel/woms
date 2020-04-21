from unittest.mock import patch, MagicMock, ANY
import whatsonms.utils as utils
import whatsonms.response as response
import tests.test_data as test_data
from whatsonms.playout_systems import DAVID


class TestBroadcast:
    @patch('whatsonms.response.metadb')
    def test_broadcast(self, p_metadb, mock_dynamodb_tables):
        p_metadb.get_metadata = MagicMock(return_value=test_data.parsed_metadata())
        resp = response.broadcast('wqxr', [], {})
        assert resp['message'] == 'No subscribers'
        assert resp['subscribers'] == []
        assert resp['stream'] == 'wqxr'

    @patch('whatsonms.response.metadb')
    def test_broadcast_with_subscribers(self, p_metadb):
        p_metadb.get_metadata = MagicMock(return_value=test_data.parsed_metadata())
        subs = [123, 456, 789]
        resp = response.broadcast('wqxr', subs, {})
        assert resp['message'] == 'Broadcast sent to subscribers'
        assert resp['subscribers'] == subs
        assert resp['stream'] == 'wqxr'

    # [jd 11/6/19] NOTE: moto3 does not currently support mocking
    #                    APIGatewayManagementAPI so I gotta do it
    #                    manually with these patches.
    @patch('whatsonms.response.metadb')
    @patch('whatsonms.response.boto3')
    def test_broadcast_notifies_ws_connections(self, boto, p_metadb):
        p_metadb.get_metadata = MagicMock(return_value=test_data.parsed_metadata())
        conn_id = 7779311
        data = {'meta': 'data'}
        response.broadcast('wqxr', [conn_id], data)
        boto.Session().client().post_to_connection.assert_called()
        boto.Session().client().post_to_connection.assert_called_with(
                Data=ANY,
                ConnectionId=conn_id)

    @patch('whatsonms.response.metadb')
    @patch('whatsonms.response.subdb')
    @patch('whatsonms.response.boto3')
    def test_removes_stale_subscriber(self, boto, subscriptiondb, metadatadb):
        metadatadb.get_metadata = MagicMock(return_value=test_data.parsed_metadata())
        def side_effect(Data="", ConnectionId=""): raise Exception("GoneException")
        boto.Session().client().post_to_connection.side_effect = side_effect
        conn_id = 7779311
        data = test_data.parsed_metadata()
        response.broadcast('wqxr', [conn_id], data)
        subscriptiondb.unsubscribe.assert_called_with(conn_id)


class TestDateTimeOperations:
    def test_convert_datetime(self):
        current_date = "2019-11-08 12:29:42.986"
        epoch_time = 1573234182
        assert epoch_time == utils.convert_time(current_date)

    def test_convert_date_and_time(self):
        current_date = "11/12/2018"
        current_time = "12:22:19"
        epoch_time = 1542043339
        assert epoch_time == utils.convert_date_time(current_date, current_time)

    def test_convert_time_to_iso(self):
        epoch = 1541519320
        iso_time = "2018-11-06T15:48:40+00:00"
        assert iso_time == utils.convert_time_to_iso(epoch)

    def test_convert_encoding(self):
        win1252str = 'Lucien-LÃ©on-Guillaume Lambert'
        utf8str = utils.convert_encoding(win1252str)
        assert utf8str == 'Lucien-Léon-Guillaume Lambert'


class TestWOMsResponse:
    def test_response(self):
        expected_resp = test_data.jsonapi_response()
        playlist_hist = next(test_data.playlist_hist())
        resp = response.Response(
            test_data.parsed_metadata(),
            playlist_hist,
            "mainstream",
            DAVID)
        assert list(resp.keys()) == list(expected_resp.keys())
        assert resp == expected_resp

    def test_id_generator(self):
        metadata = test_data.parsed_metadata()
        id_ = response.generate_id(metadata['mm_uid'], metadata['epoch_start_time'], "wqxr")
        assert id_ == "wqxr_1583789083_110813"
