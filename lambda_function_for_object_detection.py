import json
import boto3
import object_detection_v2 as od

s3_client = boto3.client('s3')
def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        image = s3_client.get_object(Bucket=bucket, Key=key)
        tags = od.detect_image_bytes(image["Body"].read())
        
        
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
