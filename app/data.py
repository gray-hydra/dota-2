"""Data access layer for items storage using DynamoDB."""

import os
import boto3
from boto3.dynamodb.conditions import Key
from app.utils import convert_floats_to_decimal, convert_decimals_to_float

# Table config
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'items')
PARTITION_KEY = 'items'  # All items share this pk value

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)


def load_items() -> list:
    """Load all items from DynamoDB, sorted by id."""
    response = table.query(
        KeyConditionExpression=Key('pk').eq(PARTITION_KEY)
    )
    return convert_decimals_to_float(response['Items'])


def save_items(items: list) -> None:
    """Save all items to DynamoDB (batch write)."""
    with table.batch_writer() as batch:
        for item in items:
            item['pk'] = PARTITION_KEY  # Ensure pk is set
            batch.put_item(Item=convert_floats_to_decimal(item))


def get_item(item_id: str) -> dict | None:
    """Get a single item by ID."""
    response = table.get_item(
        Key={'pk': PARTITION_KEY, 'id': item_id}
    )
    item = response.get('Item')
    return convert_decimals_to_float(item) if item else None


def update_item(item_id: str, updates: dict) -> dict | None:
    """Update a single item."""
    # Build update expression
    update_expr = 'SET ' + ', '.join(f'#{k} = :{k}' for k in updates.keys())
    expr_names = {f'#{k}': k for k in updates.keys()}
    expr_values = convert_floats_to_decimal({f':{k}': v for k, v in updates.items()})

    response = table.update_item(
        Key={'pk': PARTITION_KEY, 'id': item_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW'
    )
    attrs = response.get('Attributes')
    return convert_decimals_to_float(attrs) if attrs else None
