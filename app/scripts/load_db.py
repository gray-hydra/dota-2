#!/usr/bin/env python3
"""Load items.json into DynamoDB table."""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import json
import boto3
from app.utils import convert_floats_to_decimal

TABLE_NAME = 'items'
PARTITION_KEY = 'items'
DATA_FILE = 'app/data/items.json'


def main():
    # Load JSON data
    with open(DATA_FILE) as f:
        items = json.load(f)

    print(f"Loaded {len(items)} items from {DATA_FILE}")

    # Connect to DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    # Batch write items
    with table.batch_writer() as batch:
        for item in items:
            # Convert floats to Decimals
            item = convert_floats_to_decimal(item)

            # Add partition key
            item['pk'] = PARTITION_KEY

            # Ensure id is a string and zero-padded
            if isinstance(item['id'], int):
                item['id'] = str(item['id']).zfill(3)

            batch.put_item(Item=item)
            print(f"  Written: {item['id']}")

    print(f"Done! Wrote {len(items)} items to {TABLE_NAME}")

if __name__ == '__main__':
    main()
