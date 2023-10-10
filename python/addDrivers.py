import boto3
import random
import string
import time

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Drivers")


def random_string(length):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


def generate_driverID():
    """Generate a unique packageID."""
    timestamp = int(time.time() * 1000)  # Current time in milliseconds
    random_digits = "".join(random.choice(string.digits) for i in range(4))
    return f"FP{timestamp}{random_digits}"


def lambda_handler(event, context):
    try:
        # Create a random driver
        driver = {
            "driver_name": random_string(10) + " " + random_string(10),
            "driverID": generate_driverID(),
            "lieferung": "null",
            "driverstatus": "available",
        }

        # Insert the driver into the DynamoDB table
        table.put_item(Item=driver)

        return {
            "statusCode": 200,
            "body": f'Successfully inserted driver with driverID {driver["driverID"]}',
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error inserting driver into DynamoDB: {str(e)}",
        }
