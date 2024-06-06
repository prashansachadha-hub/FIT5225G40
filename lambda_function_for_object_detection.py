import json
import boto3
import object_detection_v2 as od
import urllib.parse

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
img_table = dynamodb.Table("imagesTable")
tag_table = dynamodb.Table("tagsTable")
mid_table = dynamodb.Table("imageTagMiddleTable")
STANDARD_FOLDER = "standard_images/"
RESIZED_FOLDER = 'resized_images/'

def group_tags(tags):
    tag_counts = {}
    for tag in tags:
        if tag in tag_counts:
            tag_counts[tag] += 1
        else:
            tag_counts[tag] = 1
    return tag_counts

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        decoded_key = urllib.parse.unquote_plus(key)
        
        # Extract username, image name and image id
        parts = decoded_key.split('/')
        username = parts[1]
        image_name = parts[2]
        image_id = image_name.split('.')[0]
        
        # Generate URLs for both standard and thumbnail images
        standard_image_url = f"https://{bucket}.s3.amazonaws.com/{decoded_key}"
        thumbnail_image_key = f"{RESIZED_FOLDER}/{username}/{image_name}"
        thumbnail_image_url = f"https://{bucket}.s3.amazonaws.com/{thumbnail_image_key}"
        
        img_table.put_item(
            Item={
                'imageID': image_id,
                'username': username,
                'standardImageUrl': standard_image_url,
                'thumbnailImageUrl': thumbnail_image_url
            }
        )
        print(f"Inserted item with imageID: {image_id}")
        
        image = s3_client.get_object(Bucket=bucket, Key=key)
        tags = od.detect_image_bytes(image["Body"].read())
        grouped_tags = group_tags(tags)
        
        # Insert unique tags into tag_table and relationships into mid_table
        for tag, count in grouped_tags.items():
            try:
                # Insert tag into tag_table
                tag_table.put_item(
                    Item={
                        'tagName': tag
                    },
                    ConditionExpression='attribute_not_exists(tagName)'  # Ensures unique tags
                )
                print(f"Inserted tag: {tag}")
            except boto3.dynamodb.conditions.ConditionalCheckFailedException:
                # Tag already exists, skip insertion
                print(f"Tag already exists: {tag}")
                
            # Insert relationship into mid_table
            mid_table.put_item(
                Item={
                    'imageID': image_id,
                    'tagName': tag,
                    'repetition': count
                }
            )
            print(f"Linked imageID: {image_id} with tag: {tag}")
        

        
        