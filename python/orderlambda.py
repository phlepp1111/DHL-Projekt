import json
import boto3

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb')

# Define the DynamoDB table name
table_name = 'Orders'  # Update with your DynamoDB table name

def lambda_handler(event, context):
    try:
        # Parse the input JSON data
        event_body = json.loads(event['body'])

        # Extract relevant data
        package_id = event_body['packageID']
        recipient_name = event_body['recipient']['name']
        sender_name = event_body['sender']['name']

        # Put the data into DynamoDB
        response = dynamodb.put_item(
            TableName=table_name,
            Item={
                'packageID': {'S': package_id},
                'RecipientName': {'S': recipient_name},
                'SenderName': {'S': sender_name}
                # Add more attributes as needed
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Data added to DynamoDB successfully!')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
