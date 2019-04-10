import json
from functools import lru_cache
from typing import Dict

import boto3

from whatsonms import config


class DB:
    """
    The DB class provides an abstraction around the simple operations
    the lambda handler must perform.

    Warning: This class will attempt to create a DynamoDB table if the
        specified table does not exist.
    """
    pkey = 'pkey'

    def __init__(self, table_name: str) -> None:
        _db = boto3.Session().resource('dynamodb')
        try:
            _db.meta.client.describe_table(TableName=table_name)
        except _db.meta.client.exceptions.ResourceNotFoundException:
            _db.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': self.pkey, 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': self.pkey, 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
            )
            _db.meta.client.get_waiter('table_exists').wait(TableName=table_name)

        self.table = _db.Table(table_name)
        self.table.load()

    def get(self, key: str) -> Dict:
        """
        Args:
            key: The key to retreive from DynamoDB.

        Returns:
            A python dictionary generated from the JSON DynamoDB value.
        """
        resp = self.table.get_item(Key={self.pkey: key})
        value = resp.get('Item', {}).get('value_')
        return json.loads(value) if value else {}

    def set(self, key: str, value: Dict) -> Dict:
        """
        Args:
            key: The key to create.
            value: The value to set the key to (will be JSON-serialized).

        Returns:
            The value that they key was set to.
        """
        self.table.update_item(
            Key={self.pkey: key},
            UpdateExpression='SET value_ = :value',
            ExpressionAttributeValues={':value': json.dumps(value, sort_keys=True)},
            ReturnValues='NONE',
        )
        return value


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
    def get(*args, **kwargs):
        return connect(config.DYNAMODB_TABLE).get(*args, **kwargs)

    @staticmethod
    def set(*args, **kwargs):
        return connect(config.DYNAMODB_TABLE).set(*args, **kwargs)
