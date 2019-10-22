import json
from functools import lru_cache
from typing import Dict, List

import boto3

from whatsonms import config


class DB:
    """
    The DB class provides an abstraction around the simple operations
    the lambda handler must perform.
    """
    stream_key = 'stream_slug'
    metadata_key = 'metadata'
    subscriber_key = 'connection_id'
    subscriber_index = 'connection_id-INDEX'

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
            if 'subscribers' in table_name:
                key_schema = [
                    {'AttributeName': self.stream_key, 'KeyType': 'HASH'},
                    {'AttributeName': self.subscriber_key, 'KeyType': 'RANGE'}
                ]
                attr_definitions = [
                    {'AttributeName': self.stream_key, 'AttributeType': 'S'},
                    {'AttributeName': self.subscriber_key, 'AttributeType': 'S'}
                ]
            elif 'metadata' in table_name:
                key_schema = [
                    {'AttributeName': self.stream_key, 'KeyType': 'HASH'}
                ]
                attr_definitions = [
                    {'AttributeName': self.stream_key, 'AttributeType': 'S'}
                ]

            _db.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attr_definitions,
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
        return metadata if metadata else {}

    def get_subscribers(self, stream: str) -> List:
        """
        Args:
            stream: The slug of the stream whose subscribers to retrieve from
            DynamoDB.

        Returns:
            A list of subscribers to that stream.
        """
        resp = self.table.query(
            KeyConditionExpression='stream_slug = :name',
            ExpressionAttributeValues={":name": {"S": stream}},
            ProjectionExpression=self.subscriber_key
        )
        subscribers = resp.get('Items', [])

        return [s["connection_id"]["S"] for s in subscribers]

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
                ':value': json.dumps(metadata, sort_keys=True)
            },
            ReturnValues='NONE',
        )
        return self.get_metadata(stream)

    def subscribe(self, stream: str, connection_id: str) -> List:
        """
        Args:
            stream: The stream slug.
            connection_id: The websocket connectionId of the user.

        Returns:
            The updated subscribers list with the new connection_id appended.
        """
        # TODO: update
        subscribers = self.table.update_item(
            Key={
                self.stream_key: stream,
            },
            UpdateExpression="ADD subscribers :value",
            ExpressionAttributeValues={":value": set([connection_id])},
            ReturnValues="ALL_NEW",
        )

        return subscribers

    def unsubscribe(self, connection_id: str) -> List:
        """
        Args:
            connection_id: The websocket connectionId of the user
        """
        pass
        # resp = self.table.query(
        #     IndexName=self.subscriber_index,
        #     KeyConditionExpression='{} = :value'.format(self.subscriber_key),
        #     ExpressionAttributeValues={':value': {'S': connection_id}},
        #     ProjectionExpression=self.subscriber_key
        # )

        # items = resp.get("Items", [])

        # TODO:
        # for item in items:
        #   delete item

        # return subscribers


@lru_cache()
def connect(table_name: str) -> DB:
    """
    This method allows an initialized DB to persist in memory, avoiding
    repeated calls to "describe_table".
    """
    return DB(table_name)


class db:
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

    @staticmethod
    def get_subscribers(*args, **kwargs):
        return connect(config.TABLE_SUBSCRIBERS).get_subscribers(*args, **kwargs)

    @staticmethod
    def subscribe(*args, **kwargs):
        return connect(config.TABLE_SUBSCRIBERS).subscribe(*args, **kwargs)

    @staticmethod
    def unsubscribe(*args, **kwargs):
        return connect(config.TABLE_SUBSCRIBERS).unsubscribe(*args, **kwargs)
