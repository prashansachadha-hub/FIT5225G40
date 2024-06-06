import json
import base64
import boto3
import object_detection_v2 as od
from boto3.dynamodb.conditions import Attr

# Define folder paths and S3 bucket name
STANDARD_FOLDER = "standard_images/"
RESIZED_FOLDER = 'resized_images/'
s3_client = boto3.client('s3')
S3_BUCKET = "fit5225-gp40-photos"
THUMBNAIL_WIDTH = 100

dynamodb = boto3.resource('dynamodb')
mid_table = dynamodb.Table("imageTagMiddleTable")
img_table = dynamodb.Table("imagesTable")

def lambda_handler(event, context):
    # Parse the incoming event data
    request_data = json.loads(event['body'])
    image_base64 = request_data['file']
    
    # Decode and process the image
    image_data = decode_base64_image(image_base64)
    tags = od.detect_image_bytes(image_data)
    grouped_tags = group_tags(tags)
    image_ids = find_images_by_tags(grouped_tags)
    
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
    

def decode_base64_image(image_base64):
    """Decode a base64 encoded image."""
    return base64.b64decode(image_base64)

def group_tags(tags):
    tag_counts = {}
    for tag in tags:
        if tag in tag_counts:
            tag_counts[tag] += 1
        else:
            tag_counts[tag] = 1
    return tag_counts

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