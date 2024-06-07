import json
import boto3
import urllib.parse

dynamodb = boto3.resource('dynamodb')
img_table = dynamodb.Table("imagesTable")
tag_table = dynamodb.Table("tagsTable")
mid_table = dynamodb.Table("imageTagMiddleTable")

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        urls = body['url']
        tags = body['tags']
        action_type = body['type']
        
        for url in urls:
            parsed_url = urllib.parse.urlparse(url)
            key = parsed_url.path.lstrip('/')
            parts = key.split('/')
            username = parts[1]
            image_name = parts[2]
            image_id = image_name.split('.')[0]
            
            if action_type == 1:
                add_tags(image_id, tags)
            elif action_type == 0:
                remove_tags(image_id, tags)
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps('Invalid type. Use 1 for add and 0 for remove.')
                }
        
        return {
            'statusCode': 200,
            'body': json.dumps('Tags modified successfully.')
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }

def add_tags(image_id, tags):
    for tag in tags:
        try:
            # Insert tag into tag_table if it doesn't exist
            tag_table.put_item(
                Item={
                    'tagName': tag
                },
                ConditionExpression='attribute_not_exists(tagName)'  # Ensures unique tags
            )
            print(f"Inserted tag: {tag}")
        except Exception as e:
            # Tag already exists, skip insertion
            print(f"Tag already exists or another error occurred: {tag} - {str(e)}")
        
        # Insert or update relationship into mid_table
        mid_table.update_item(
            Key={
                'imageID': image_id,
                'tagName': tag
            },
            UpdateExpression="set repetition = if_not_exists(repetition, :start) + :inc",
            ExpressionAttributeValues={
                ':start': 0,
                ':inc': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Linked imageID: {image_id} with tag: {tag}")

def remove_tags(image_id, tags):
    for tag in tags:
        try:
            # Decrement the count by 1
            response = mid_table.update_item(
                Key={
                    'imageID': image_id,
                    'tagName': tag
                },
                UpdateExpression="set repetition = repetition - :dec",
                ConditionExpression="repetition > :zero",
                ExpressionAttributeValues={
                    ':dec': 1,
                    ':zero': 0
                },
                ReturnValues="UPDATED_NEW"
            )
            # If the count reaches 0, remove the record
            if response['Attributes']['repetition'] <= 0:
                mid_table.delete_item(
                    Key={
                        'imageID': image_id,
                        'tagName': tag
                    }
                )
                print(f"Removed link between imageID: {image_id} and tag: {tag} because count reached 0")
            else:
                print(f"Decremented repetition for imageID: {image_id} and tag: {tag}")
        except Exception as e:
            print(f"Error decrementing link: {image_id} - {tag} - {str(e)}")