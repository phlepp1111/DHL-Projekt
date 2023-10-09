import boto3
import random
import string
import time
from datetime import date
import os

# Initialize the DynamoDB resource
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Orders")  # Replace 'YourTableName' with your table's name
sqs = boto3.client("sqs")
sqs_queue_url = os.environ["SQS_QUEUE_URL"]
message_group_id = "order-sqs-group"


def random_string(length):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters + string.digits + " "
    return "".join(random.choice(letters) for i in range(length))


def random_phone():
    """Generate a random phone number."""
    return "".join(random.choice(string.digits) for i in range(10))


def generate_packageID():
    """Generate a unique packageID."""
    timestamp = int(time.time() * 1000)  # Current time in milliseconds
    random_digits = "".join(random.choice(string.digits) for i in range(4))
    return f"FP{timestamp}{random_digits}"


def lambda_handler(event, context):
    try:
        # Create a random item
        item = {
            "recipient_name": random_string(10),
            "recipient_address": random_string(25),
            "recipient_phone": random_phone(),
            "sender_name": random_string(10),
            "sender_address": random_string(25),
            "sender_phone": random_phone(),
            "dimensions_length": random.randint(1, 100),
            "dimensions_width": random.randint(1, 100),
            "dimensions_height": random.randint(1, 100),
            "weight": random.randint(1, 50),
            "packageID": generate_packageID(),
            "date": str(date.today()),  # Insert today's date
            "insurance_type": random.choice(["Basic", "Premium", "Gold"]),
            "insurance_value": random.randint(1, 5000),
            "restrictions": random.choice(
                ["Sperrgut", "Zerbrechlich", "Liquid", "Flammable"]
            ),  # Two random restrictions
            "value": random.randint(1, 1000),
        }

        # Insert the item into the DynamoDB table
        table.put_item(Item=item)

        message_body = (
            "ItemID: "
            + item["packageID"]
            + ", Restrictions: "
            + item["restrictions"]
            + ", Date: "
            + item["date"]
        )
        # sqs.Queue(sqs_queue_url).send_message(MessageBody=message_body)
        sqs.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=message_body,
            MessageGroupId=message_group_id,
        )

        return {
            "statusCode": 200,
            "body": f'Successfully inserted item with packageID {item["packageID"]} and added to SQS queue',
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error inserting item into DynamoDB: {str(e)}",
        }
