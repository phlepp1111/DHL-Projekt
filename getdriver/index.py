import json

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    # Process the DynamoDB records as needed
    return {"statusCode": 200, "body": "Processed records"}