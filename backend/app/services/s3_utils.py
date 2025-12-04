"""S3/MinIO utility functions for object storage."""
import boto3
import os
from typing import Optional
from uuid import uuid4


def get_s3_client():
    """Get configured S3 client for MinIO."""
    endpoint_url = f"http://{os.getenv('MINIO_ENDPOINT', 'minio:9000')}"
    
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minio"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minio123"),
        region_name="us-east-1"  # Required for boto3
    )


def upload_file(file_data: bytes, filename: str, bucket: str = "realestate") -> str:
    """
    Upload file to S3/MinIO.
    
    Args:
        file_data: File bytes
        filename: Original filename
        bucket: S3 bucket name
        
    Returns:
        S3 path string (s3://bucket/key)
    """
    s3 = get_s3_client()
    
    # Generate unique filename
    unique_filename = f"{uuid4().hex}_{filename}"
    
    # Ensure bucket exists
    try:
        s3.create_bucket(Bucket=bucket)
    except s3.exceptions.BucketAlreadyExists:
        pass
    except Exception:
        # Bucket might already exist or other error
        pass
    
    # Upload file
    s3.put_object(Bucket=bucket, Key=unique_filename, Body=file_data)
    
    return f"s3://{bucket}/{unique_filename}"


def get_presigned_url(s3_path: str, expiration: int = 3600) -> str:
    """
    Generate a presigned URL for temporary access.
    
    Args:
        s3_path: S3 path (s3://bucket/key)
        expiration: URL expiration time in seconds
        
    Returns:
        Presigned URL string
    """
    s3 = get_s3_client()
    
    # Parse s3://bucket/key
    if s3_path.startswith("s3://"):
        parts = s3_path[5:].split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
    else:
        raise ValueError(f"Invalid S3 path: {s3_path}")
    
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expiration
    )


def download_file(s3_path: str) -> bytes:
    """
    Download file from S3/MinIO.
    
    Args:
        s3_path: S3 path (s3://bucket/key)
        
    Returns:
        File bytes
    """
    s3 = get_s3_client()
    
    # Parse s3://bucket/key
    if s3_path.startswith("s3://"):
        parts = s3_path[5:].split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
    else:
        raise ValueError(f"Invalid S3 path: {s3_path}")
    
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()

