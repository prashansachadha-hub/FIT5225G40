import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
img_table = dynamodb.Table("imagesTable")

def lambda_handler(event, context):
    body = json.loads(event['body'])
    thumbnail_url = body.get('thumbnail_url')
    
    if not thumbnail_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid request: thumbnail_url is required'})
        }
    
    # Retrieve the standard image URL from img_table
    response = img_table.scan(
        FilterExpression=Attr('thumbnailImageUrl').eq(thumbnail_url)
    )
    
    if 'Items' not in response or not response['Items']:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'No image found for the given thumbnail URL'})
        }
    
    standard_image_url = response['Items'][0].get('standardImageUrl')
    
    if not standard_image_url:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'Standard image URL not found for the given thumbnail URL'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'standardImageUrl': standard_image_url})
    }
