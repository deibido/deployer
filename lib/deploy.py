import os
import subprocess

import boto3


class ObjectUploadException(BaseException):
    pass


def s3_deploy(bucket_name: str) -> str:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    bucket_web = s3.BucketWebsite(bucket_name)

    response = bucket.create(
        ACL="public-read",
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1",
        },
    )

    response2 = bucket_web.put(
        WebsiteConfiguration={
            'IndexDocument': {
                    'Suffix': 'index.html',
            },
        },
    )

    # Use subprocess and the awscli because the `sync` command
    # hasn't been implemented in boto3 and is much faster than
    # copying objects one by one
    upload = subprocess.Popen(
        ["aws", "s3", "sync", f"{os.getcwd()}/web/", f"s3://{bucket_name}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, error = upload.communicate()

    if error.decode("utf-8") != "":
        raise ObjectUploadException(f"Sync to S3 failed: {error.decode('utf-8')}")

    return "Fix this"
