import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
img_table = dynamodb.Table("imagesTable")
mid_table = dynamodb.Table("imageTagMiddleTable")

def lambda_handler(event, context):
    body = json.loads(event['body'])
    required_tags = body.get('tags', {})
    
    # Find imageIDs that meet the tag requirements
    image_ids = find_images_by_tags(required_tags)
    
    if not image_ids:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'No images found matching the criteria'})
        }
    
    # Retrieve image details from img_table
    images = []
    for image_id in image_ids:
        response = img_table.get_item(Key={'imageID': image_id})
        if 'Item' in response:
            images.append(response['Item'])
    
    return {
        'statusCode': 200,
        'body': json.dumps(images)
    }

def find_images_by_tags(required_tags):
    image_ids = set()
    
    for tag, min_repetition in required_tags.items():
        response = mid_table.scan(
            FilterExpression=Attr('tagName').eq(tag) & Attr('repetition').gte(min_repetition)
        )
        tag_image_ids = {item['imageID'] for item in response['Items']}
        
        if not image_ids:
            image_ids = tag_image_ids
        else:
            image_ids &= tag_image_ids
    
    return image_ids

