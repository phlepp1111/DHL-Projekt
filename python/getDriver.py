import boto3
import json
import os

sqs = boto3.client("sqs")
sqs_queue_url = os.environ["SQS_QUEUE_URL"]

dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    try:
        driver_response = dynamodb.scan(
            TableName="Drivers",
            FilterExpression="attribute_exists(driverstatus) AND #s = :available",
            ExpressionAttributeNames={"#s": "driverstatus"},
            ExpressionAttributeValues={":available": {"S": "available"}},
        )
        available_drivers = driver_response.get("Items", [])
        if available_drivers:
            first_available_driver = available_drivers[0]
            # Display information about the first available driver
            print(f"First available driver: {first_available_driver}")

            sqs_response = sqs.receive_message(
                QueueUrl=sqs_queue_url,
                MaxNumberOfMessages=1,  # Retrieve a single message
                MessageAttributeNames=["All"],
                AttributeNames=["All"],
            )
            messages = sqs_response.get("Messages", [])
            if messages:
                first_message = messages[0]
                message_body = json.loads(first_message["Body"])
                print(f"Message body: {message_body}")

                sqs.delete_message(
                    QueueUrl=sqs_queue_url, ReceiptHandle=first_message["ReceiptHandle"]
                )
            else:
                return {
                    "statusCode": 500,
                    "body": f"Error: no orders found",
                }

            return {
                "statusCode": 200,
                "body": f"New order: {message_body.get('packageID')} is matched with driver {first_available_driver.get('driverID')}",
            }
        else:
            return {
                "statusCode": 500,
                "body": f"Error: no available drivers found",
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}",
        }
