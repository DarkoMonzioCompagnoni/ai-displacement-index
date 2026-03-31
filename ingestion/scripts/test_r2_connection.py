import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
    region_name="auto",
)

bucket = os.getenv("R2_BUCKET_NAME")

# Upload a small test file
s3.put_object(Bucket=bucket, Key="test/connection_check.txt", Body=b"R2 connection OK")
print("Upload successful")

# Confirm it's there
response = s3.list_objects_v2(Bucket=bucket, Prefix="test/")
for obj in response.get("Contents", []):
    print(f"Found: {obj['Key']}")
