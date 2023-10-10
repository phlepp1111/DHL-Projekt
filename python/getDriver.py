import boto3
import json
import os

sqs = boto3.client("sqs")
sqs_queue_url = os.environ["SQS_QUEUE_URL"]

dynamodb = boto3.client("dynamodb")


def update_driver_status(driver_id, package_id, new_status):
    # Update the driver status in the "Drivers" DynamoDB table
    status_response = dynamodb.update_item(
        TableName="Drivers",
        Key={"driverID": driver_id},
        UpdateExpression="SET driverstatus = :new_status",
        ExpressionAttributeValues={":new_status": {"S": new_status}},
    )
    lieferung_response = dynamodb.update_item(
        TableName="Drivers",
        Key={"driverID": driver_id},
        UpdateExpression="SET lieferung = :package_id",
        ExpressionAttributeValues={":package_id": {"S": package_id}},
    )


def update_order_status(package_id, new_status):
    # Update the order status in the "Orders" DynamoDB table
    response = dynamodb.update_item(
        TableName="Orders",
        Key={"packageID": {"S": package_id}},
        UpdateExpression="SET lieferstatus = :new_status",
        ExpressionAttributeValues={":new_status": {"S": new_status}},
    )


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

                package_id = message_body.get("packageID")
                driver_id = first_available_driver.get("driverID")

                update_driver_status(driver_id, package_id, "not available")
                update_order_status(package_id, f"bei Fahrer {driver_id}")

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
                "body": f"New order: {package_id} is matched with driver {driver_id}",
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
