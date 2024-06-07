import json
import boto3
import urllib.parse

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
img_table = dynamodb.Table("imagesTable")
tag_table = dynamodb.Table("tagsTable")
mid_table = dynamodb.Table("imageTagMiddleTable")

def lambda_handler(event, context):
    try:
        request_data = json.loads(event['body'])
        urls = request_data['url']
        
        for url in urls:
            # Parse S3 bucket and key from the URL
            parsed_url = urllib.parse.urlparse(url)
            bucket = parsed_url.netloc.split('.')[0]
            key = parsed_url.path.lstrip('/')
            
            # Extract username, image name and image id
            parts = key.split('/')
            username = parts[1]
            image_name = parts[2]
            image_id = image_name.split('.')[0]
            
            # Delete the image from S3
            s3_client.delete_object(Bucket=bucket, Key=key)
            print(f"Deleted object from S3: {key}")
            
            # Remove the image from img_table
            img_table.delete_item(
                Key={
                    'imageID': image_id
                }
            )
            print(f"Deleted item from img_table: {image_id}")
            
            # Remove the relationships from mid_table
            response = mid_table.query(
                IndexName='tagName-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('imageID').eq(image_id)
            )
            for item in response['Items']:
                mid_table.delete_item(
                    Key={
                        'imageID': item['imageID'],
                        'tagName': item['tagName']
                    }
                )
                print(f"Deleted item from mid_table: {item['imageID']} - {item['tagName']}")
            
            # Optionally, you might want to clean up unused tags in the tag_table
            
        return {
            'statusCode': 200,
            'body': json.dumps("Images and related data removed successfully")
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps("An error occurred while processing the request")
        }
