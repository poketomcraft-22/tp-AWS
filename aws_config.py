import boto3

AWS_ACCESS_KEY_ID = "TON_ACCESS_KEY"
AWS_SECRET_ACCESS_KEY = "TON_SECRET_KEY"
AWS_REGION = "us-east-1"  # ← ici tu mets la région de tes buckets

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

