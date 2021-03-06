from whatsonms.dynamodb import MetadataDB, SubscriberDB
from whatsonms import config


class TestMetadataDDB:
    def test_connect_to_metadata_table(self, mock_thin_ddb):
        table_name = config.TABLE_METADATA
        metadatabase = MetadataDB(table_name)
        md = metadatabase.get_metadata('wqxr')
        assert not md

    def test_set_and_get_metadata(self, mock_thin_ddb):
        slug = 'wqxr'
        metadata = {'Artist': 'Soccer Mommy'}
        metadatabase = MetadataDB(config.TABLE_METADATA)
        metadatabase.set_metadata(slug, metadata)
        md = metadatabase.get_metadata(slug)
        assert md['Artist'] == 'Soccer Mommy'


class TestSubscribersDDB:
    def test_connect_to_subscriber_table(self, mock_thin_ddb):
        table_name = config.TABLE_SUBSCRIBERS
        subdb = SubscriberDB(table_name)
        md = subdb.get_subscribers('wqxr')
        assert md == []

    def test_add_and_get_subscriber_in_table(self, mock_thin_ddb):
        slug = 'wqxr'
        my_id = 'jordan is cool'
        subdb = SubscriberDB(config.TABLE_SUBSCRIBERS)
        response = subdb.subscribe(slug, my_id)
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200
        subs = subdb.get_subscribers(slug)
        assert my_id in subs

    def test_add_and_remove_subscriber_from_table(self, mock_thin_ddb):
        slug = 'wqxr'
        my_id = 'jordan is cool'
        subdb = SubscriberDB(config.TABLE_SUBSCRIBERS)
        subdb.subscribe(slug, my_id)
        subs = subdb.get_subscribers(slug)
        assert my_id in subs
        subdb.unsubscribe(my_id)
        subs = subdb.get_subscribers(slug)
        assert my_id not in subs
