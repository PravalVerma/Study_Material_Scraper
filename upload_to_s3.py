import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Configuration - Replace these with your actual details, or set them as Environment Variables
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID', 'YOUR_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'YOUR_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'YOUR_REGION')
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'YOUR_BUCKET_NAME')

# The folder you want to upload
FOLDER_TO_UPLOAD = "NCERT"

def upload_folder_to_s3(local_dir, bucket_name):
    # Initialize the S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    if not os.path.exists(local_dir):
        print(f"Error: Directory '{local_dir}' does not exist.")
        return

    print(f"Starting upload to S3 Bucket: {bucket_name}")
    uploaded_count = 0

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            
            # The S3 key (path in the bucket) should be a forward-slash separated path
            # We replace Windows backslashes with forward slashes for S3 consistency
            s3_key = os.path.relpath(local_path, start=".").replace("\\", "/")

            try:
                print(f"Uploading: {s3_key} ...", end=" ")
                s3_client.upload_file(local_path, bucket_name, s3_key)
                print("Done!")
                uploaded_count += 1
            except FileNotFoundError:
                print("Failed (File not found)")
            except NoCredentialsError:
                print("\nError: AWS credentials not found or invalid.")
                return
            except ClientError as e:
                print(f"Failed (S3 Client Error: {e})")
                
    print(f"\nUpload complete! Successfully uploaded {uploaded_count} files to s3://{bucket_name}/{FOLDER_TO_UPLOAD}/")

if __name__ == "__main__":
    if AWS_ACCESS_KEY == 'YOUR_ACCESS_KEY':
        print("Please update your AWS credentials in the script or set them as environment variables.")
    else:
        upload_folder_to_s3(FOLDER_TO_UPLOAD, BUCKET_NAME)
