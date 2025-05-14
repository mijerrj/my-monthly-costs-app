import os
import json
import uuid
from datetime import datetime
import boto3
from botocore.client import Config

# Load env vars
S3_ENDPOINT    = os.getenv("AWS_ENDPOINT_URL")
S3_REGION      = os.getenv("AWS_REGION")
S3_ACCESS_KEY  = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY  = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET      = os.getenv("S3_BUCKET_NAME")

# Create an S3-compatible client
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(signature_version="s3v4")
)

def log_audit(event_type: str, payload: dict):
    """
    Write an audit entry to S3 as a JSON file.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": timestamp,
        "event": event_type,
        "payload": payload
    }
    key = f"audit/{timestamp[:10]}/{record['id']}.json"
    body = json.dumps(record).encode("utf-8")
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body, ContentType="application/json")
