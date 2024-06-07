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
    
    # Retrieve thumbnail images from img_table
    thumbnail_images = []
    for image_id in image_ids:
        response = img_table.get_item(Key={'imageID': image_id})
        if 'Item' in response:
            thumbnail_images.append(response['Item']['thumbnailImageUrl'])
    
    return {
        'statusCode': 200,
        'body': json.dumps(thumbnail_images)
    }

def find_images_by_tags(required_tags):
    image_ids = set()
    
    for tag, min_repetition in required_tags.items():
        response = mid_table.scan(
            FilterExpression=Attr('tagName').eq(tag) & Attr('repetition').gte(min_repetition)
        )
        tag_image_ids = {item['imageID'] for item in response['Items']}
        print(f"tag: {tag}, min_repetition: {min_repetition}, tag_image_ids {tag_image_ids}")
        
        # If at any point the intersection is empty, the result is empty
        if not tag_image_ids:
            image_ids = set()
            break
        
        if not image_ids:
            image_ids = tag_image_ids
        else:
            image_ids &= tag_image_ids
            
    print(f"final image_ids: {image_ids}")
    return image_ids

