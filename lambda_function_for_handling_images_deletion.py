import boto3
import json
import urllib.parse



# Initialize AWS services
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# DynamoDB tables
img_table = dynamodb.Table("imagesTable")
mid_table = dynamodb.Table("imageTagMiddleTable")

def lambda_handler(event, context):
    urls = json.loads(event['body'])['url']
    
    for url in urls:
        # Parse the URL to get the bucket name and key
        parsed_url = urllib.parse.urlparse(url)
        bucket = parsed_url.netloc.split('.')[0]
        key = parsed_url.path.lstrip('/')

        # Delete the image from S3
        s3_client.delete_object(Bucket=bucket, Key=key)
        print(f"Deleted from S3: {key}")
        
        standard_key = 'standard_images/' + '/'.join(key.split('/')[1:])
        s3_client.delete_object(Bucket=bucket, Key=standard_key)
        print(f"Deleted from S3: {standard_key}")
        
        image_id = key.split('/')[-1].split('.')[0]

        # Delete associated records from DynamoDB
        # Delete image record
        img_table.delete_item(
            Key={
                'imageID': image_id
            }
        )
        print(f"Deleted from DynamoDB img_table: {image_id}")
        
        # Query and delete associated tag records from mid_table
        response = mid_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('imageID').eq(image_id)
        )
        for item in response['Items']:
            mid_table.delete_item(
                Key={
                    'imageID': item['imageID'],
                    'tagName': item['tagName']
                }
            )
            print(f"Deleted from DynamoDB mid_table: {item['imageID']} tagged {item['tagName']}")

    return {
        'statusCode': 200,
        'body': json.dumps("Images and related data removed successfully")
    }
