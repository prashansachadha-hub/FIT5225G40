import json
import boto3
import object_detection_v2 as od

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = "pixtag"

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
        image_name = key.split()[2]
        
        image = s3_client.get_object(Bucket=bucket, Key=key)
        tags = od.detect_image_bytes(image["Body"].read())
        grouped_tags = group_tags(tags)
        
        
        table = dynamodb.Table(TABLE_NAME)
        table.put_item()