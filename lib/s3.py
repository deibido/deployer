import os
import subprocess

import boto3
from botocore.exceptions import ClientError as BotoError


class ObjectUploadException(BaseException):
    pass


def deploy(bucket_name: str) -> None:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    bucket_web = s3.BucketWebsite(bucket_name)

    try:
        bucket.create(
            ACL="public-read",
            CreateBucketConfiguration={
                "LocationConstraint": "eu-west-1",
            },
        )
        bucket_web.put(
            WebsiteConfiguration={
                'IndexDocument': {
                        'Suffix': 'index.html',
                },
            },
        )
    except BotoError as err:
        print(f"Creation of bucket website failed.")
        raise

    update(bucket_name)


def update(bucket_name):
    # Use subprocess and the awscli because the `sync` command
    # hasn't been implemented in boto3 and is much faster than
    # copying objects one by one
    upload = subprocess.Popen(
        [
            "aws",
            "s3",
            "sync",
            f"{os.getcwd()}/web/",
            f"s3://{bucket_name}",
            "--acl",
            "public-read",
            "--delete",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, error = upload.communicate()

    if error.decode("utf-8") != "":
        raise ObjectUploadException(f"Sync to S3 failed: {error.decode('utf-8')}")


def teardown(bucket_name: str) -> None:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)

    try:
        bucket.objects.delete()
        bucket.delete()
    except BotoError as err:
        print(f"Deletion of bucket website failed due to: {err}")
