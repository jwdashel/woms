from functools import lru_cache
from typing import Dict, List

import boto3
from boto3.dynamodb.conditions import Key

from whatsonms import config


class DB:
    """
    The DB class provides an abstraction around the simple operations
    the lambda handler must perform.
    """
    pass


class MetadataDB(DB):
    stream_key = 'stream_slug'
    metadata_key = 'metadata'

    def __init__(self, table_name: str) -> None:
        _db = boto3.Session().resource('dynamodb')
        try:
            _db.meta.client.describe_table(TableName=table_name)
        except _db.meta.client.exceptions.ResourceNotFoundException:
            # [10/22/19 - jd] this create statement is required for tests.
            # We thought we could get rid of it (since this is infrastructure
            # defined in application code ???) but without it, test tables
            # don't get created when running pytest. Maybe there is a solution
            # but I am fine leaving it like this for now.
            if config.ENV != 'demo' and config.ENV != 'prod':
                _db.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': self.stream_key, 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': self.stream_key, 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5
                    },
                )
                _db.meta.client.get_waiter('table_exists').wait(TableName=table_name)

        self.table = _db.Table(table_name)
        self.table.load()

    def get_metadata(self, stream: str) -> Dict:
        """
        Args:
            stream: The slug of the stream whose metadata to retrieve from
            DynamoDB.

        Returns:
            A python dictionary generated from the JSON DynamoDB value.
        """
        metadata = self.table.get_item(
            Key={self.stream_key: stream},
            # return metadata attribute only:
            ProjectionExpression=self.metadata_key
        )
        try:
            return metadata['Item']['metadata']
        except KeyError:
            return {}

    def set_metadata(self, stream: str, metadata: Dict) -> Dict:
        """
        Args:
            stream: The stream to create or update.
            metadata: The value to set the key to (will be JSON-serialized).

        Returns:
            The value that they key was set to.
        """
        self.table.update_item(
            Key={
                self.stream_key: stream,
            },
            UpdateExpression='SET metadata = :value',
            ExpressionAttributeValues={
                ':value': metadata
            },
            ReturnValues='NONE',
        )
        return self.get_metadata(stream)


class SubscriberDB(DB):
    stream_key = 'stream_slug'
    subscriber_key = 'connection_id'
    stream_index = 'stream-INDEX'

    def __init__(self, table_name: str) -> None:
        _db = boto3.Session().resource('dynamodb')
        try:
            _db.meta.client.describe_table(TableName=table_name)
        except _db.meta.client.exceptions.ResourceNotFoundException:
            # [10/22/19 - jd] this create statement is required for tests.
            # We thought we could get rid of it (since this is infrastructure
            # defined in application code ???) but without it, test tables
            # don't get created when running pytest. Maybe there is a solution
            # but I am fine leaving it like this for now.
            key_schema = [
                {'AttributeName': self.subscriber_key, 'KeyType': 'HASH'}
            ]
            attr_definitions = [
                {'AttributeName': self.stream_key, 'AttributeType': 'S'},
                {'AttributeName': self.subscriber_key, 'AttributeType': 'S'}
            ]
            gsi = [
                {
                    'IndexName': self.stream_index,
                    'KeySchema': [
                        {'AttributeName': self.stream_key, 'KeyType': 'HASH'},
                        {'AttributeName': self.subscriber_key, 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'KEYS_ONLY'}
                }
            ]

            _db.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                GlobalSecondaryIndexes=gsi,
                AttributeDefinitions=attr_definitions,
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5
                },
            )
            _db.meta.client.get_waiter('table_exists').wait(TableName=table_name)

        self.table = _db.Table(table_name)
        self.table.load()

    def get_subscribers(self, stream: str) -> List:
        """
        Args:
            stream: The slug of the stream whose subscribers to retrieve from
            DynamoDB.

        Returns:
            A list of subscribers to that stream.
        """
        resp = self.table.query(
            IndexName=self.stream_index,
            KeyConditionExpression=Key(self.stream_key).eq(stream)
        )
        subscribers = resp.get('Items', [])

        # return [s["connection_id"]["S"] for s in subscribers]
        # will amzn give back the weird type bs? if so, need to reflect in tests
        return [s["connection_id"] for s in subscribers]

    def subscribe(self, stream: str, connection_id: str) -> List:
        """
        Args:
            stream: The stream slug.
            connection_id: The websocket connectionId of the user.

        Returns:
            The updated subscribers list with the new connection_id appended.
        """
        return self.table.put_item(
            Item={
                self.stream_key: stream,
                self.subscriber_key: connection_id
            },
        )

    def unsubscribe(self, connection_id: str) -> List:
        """
        Args:
            connection_id: The websocket connectionId of the user
        """
        return self.table.delete_item(
            Key={self.subscriber_key: connection_id}
        )


@lru_cache()
def connect(table_name: str) -> DB:
    """
    This method allows an initialized DB to persist in memory, avoiding
    repeated calls to "describe_table".
    """
    if 'metadata' in table_name:
        return MetadataDB(table_name)
    elif 'subscribers' in table_name:
        return SubscriberDB(table_name)


class metadb:
    """
    Provides a lazy-loading interface for the default DynamoDB table.
    Use this to avoid import and passing config in every file.

    Usage:

        from whatsonms.dynamodb import db
        db.get(...)
        db.set(...)
    """
    @staticmethod
    def get_metadata(*args, **kwargs):
        return connect(config.TABLE_METADATA).get_metadata(*args, **kwargs)

    @staticmethod
    def set_metadata(*args, **kwargs):
        return connect(config.TABLE_METADATA).set_metadata(*args, **kwargs)


class subdb:
    """
    Provides a lazy-loading interface for the default DynamoDB table.
    Use this to avoid import and passing config in every file.

    Usage:

        from whatsonms.dynamodb import db
        db.get(...)
        db.set(...)
    """
    @staticmethod
    def get_subscribers(*args, **kwargs):
        return connect(config.TABLE_SUBSCRIBERS).get_subscribers(*args, **kwargs)

    @staticmethod
    def subscribe(*args, **kwargs):
        return connect(config.TABLE_SUBSCRIBERS).subscribe(*args, **kwargs)

    @staticmethod
    def unsubscribe(*args, **kwargs):
        return connect(config.TABLE_SUBSCRIBERS).unsubscribe(*args, **kwargs)
