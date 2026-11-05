import boto3
import json
import os
import uuid
import io
from PIL import Image, ImageOps; 

s3 = boto3.client('s3')

def s3_thumbnail_generator(event, context):
    print("Event::: ", event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    img_size = event['Records'][0]['s3']['object']['size']  # Set the desired thumbnail size

    if (not key.endswith("_thumbnail.png")):

        image = get_s3_image(bucket, key)
        
        thumbnail = image_to_thumbnail(image)
        
        thumbnail_key = new_filename(key)

        # s3.put_object(Bucket=bucket, Key=thumbnail_key, Body=thumbnail, ContentType='image/png')

        url = upload_to_s3(bucket, thumbnail_key, thumbnail, img_size);

        print("Image::: ", url)
        return url

def get_s3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    image_data = response['Body'].read()
    image = Image.open(io.BytesIO(image_data))
    return image

def image_to_thumbnail(image):
    # Create a thumbnail of the image
    thumbnail_size = (128, 128)  # Set the desired thumbnail size
    image.thumbnail(thumbnail_size)
    
    # Create a new image with a white background
    thumbnail = Image.new('RGB', thumbnail_size, (255, 255, 255))
    
    # Calculate the position to paste the resized image onto the white background
    x_offset = (thumbnail_size[0] - image.width) // 2
    y_offset = (thumbnail_size[1] - image.height) // 2
    
    # Paste the resized image onto the white background
    thumbnail.paste(image, (x_offset, y_offset))
    
    # Save the thumbnail to a BytesIO object
    thumbnail_bytes = io.BytesIO()
    thumbnail.save(thumbnail_bytes, format='PNG')
    thumbnail_bytes.seek(0)
    
    return thumbnail_bytes

def new_filename(key):
    # Generate a new filename for the thumbnail
    base_name, ext = os.path.splitext(key)
    new_key = f"{base_name}_thumbnail.png"
    return new_key

def upload_to_s3(bucket, thumbnail_key, thumbnail, img_size):
    # Upload the thumbnail to S3
    s3.put_object(Bucket=bucket, Key=thumbnail_key, Body=thumbnail, ContentType='image/png')
    
    # Generate a pre-signed URL for the uploaded thumbnail
    url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': thumbnail_key}, ExpiresIn=3600)
    
    return url


