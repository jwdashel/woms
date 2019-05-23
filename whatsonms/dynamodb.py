import json
from functools import lru_cache
from typing import Dict, List

import boto3
from boto3.dynamodb.conditions import Attr

from whatsonms import config


class DB:
    """
    The DB class provides an abstraction around the simple operations
    the lambda handler must perform.

    Warning: This class will attempt to create a DynamoDB table if the
        specified table does not exist.
    """
    stream_key = 'stream'
    data_type_key = 'datatype'
    type_metadata = 'metadata'
    type_subscribers = 'subscribers'

    def __init__(self, table_name: str) -> None:
        _db = boto3.Session().resource('dynamodb')
        try:
            _db.meta.client.describe_table(TableName=table_name)
        except _db.meta.client.exceptions.ResourceNotFoundException:
            _db.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': self.stream_key, 'KeyType': 'HASH'},
                    {'AttributeName': self.data_type_key, 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': self.stream_key, 'AttributeType': 'S'},
                    {'AttributeName': self.data_type_key, 'AttributeType': 'S'}
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
            stream: The slug of the stream to retreive from DynamoDB.

        Returns:
            A python dictionary generated from the JSON DynamoDB value.
        """
        metadata = self.table.get_item(
            Key={
                self.stream_key: stream,
                self.data_type_key: self.type_metadata
            },
            # return metadata attribute only:
            ProjectionExpression=self.type_metadata
        )
        return metadata if metadata else {}

    def get_subscribers(self, stream: str) -> List:
        """
        """
        resp = self.table.get_item(
            Key={
                self.stream_key: stream,
                self.data_type_key: self.type_subscribers
            },
            ProjectionExpression=self.type_subscribers
        )
        subscribers = resp['Item']['subscribers']

        return subscribers

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
                self.data_type_key: self.type_metadata
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
        subscribers = self.table.update_item(
            Key={
                self.stream_key: stream,
                self.data_type_key: self.type_subscribers
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

        Returns:
            The updated subscribers list with the connection_id removed.
        """

        resp = self.table.scan(
            FilterExpression=Attr('subscribers').contains(connection_id)
        )
        items = resp['Items']

        for item in items:
            subscribers = self.table.update_item(
                Key={
                    self.stream_key: item[self.stream_key],
                    self.data_type_key: self.type_subscribers
                },
                UpdateExpression='DELETE subscribers :value',
                ExpressionAttributeValues={':value': set([connection_id])},
                ReturnValues='ALL_NEW',
            )

        return subscribers


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
        return connect(config.DYNAMODB_TABLE).get_metadata(*args, **kwargs)

    @staticmethod
    def set_metadata(*args, **kwargs):
        return connect(config.DYNAMODB_TABLE).set_metadata(*args, **kwargs)

    @staticmethod
    def get_subscribers(*args, **kwargs):
        return connect(config.DYNAMODB_TABLE).get_subscribers(*args, **kwargs)

    @staticmethod
    def subscribe(*args, **kwargs):
        return connect(config.DYNAMODB_TABLE).subscribe(*args, **kwargs)

    @staticmethod
    def unsubscribe(*args, **kwargs):
        return connect(config.DYNAMODB_TABLE).unsubscribe(*args, **kwargs)
