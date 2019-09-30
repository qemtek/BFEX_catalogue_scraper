import logging

import boto3
from botocore.exceptions import ClientError
from configuration import s3_credentials


# Upload a new file
def upload_to_s3(local_path, s3_path, bucket="betfair-exchange-qemtek"):
    """Upload a file to an S3 bucket

    :param local_path: File to upload
    :param bucket: Bucket to upload to
    :param s3_path: Path inside S3 to store the data
    """

    # Upload the file
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=s3_credentials["access_key"],
        aws_secret_access_key=s3_credentials["secret_key"],
    )
    try:
        s3_client.upload_file(local_path, bucket, s3_path)
    except ClientError as e:
        logging.error(e)
        print(e)


def download_from_s3(local_path, s3_path, bucket="betfair-exchange-qemtek"):
    """Download a file from an S3 bucket

        :param local_path: Path to save the file
        :param bucket: Bucket to upload to
        :param s3_path: S3 path
        """

    s3 = boto3.client(
        "s3",
        aws_access_key_id=s3_credentials["access_key"],
        aws_secret_access_key=s3_credentials["secret_key"],
    )
    s3.download_file(bucket, s3_path, local_path)


def s3_dir_exists(s3_path, bucket="betfair-exchange-qemtek"):
    """Check if a file exists in a user-supplied S3 directory

    :param s3_path: The path to search for the file
    :param bucket: The name of the S3 bucket
    """

    s3 = boto3.resource(
        "s3",
        aws_access_key_id=s3_credentials["access_key"],
        aws_secret_access_key=s3_credentials["secret_key"],
    )

    try:
        s3.Object(bucket, s3_path).load()
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            # The object does not exist.
            return False
        else:
            # Something else has gone wrong.
            raise
    else:
        # The object does exist.
        return True


# Lists all files in a given S3 directory
def list_files(prefix, bucket_name="betfair-exchange-qemtek"):
    """List files in specific S3 URL"""
    client = boto3.client(
        "s3",
        aws_access_key_id=s3_credentials.get("access_key"),
        aws_secret_access_key=s3_credentials.get("secret_key"),
    )
    response = client.list_objects(Bucket=bucket_name, Prefix=prefix)
    output = []
    for content in response.get("Contents", []):
        output.append(content.get("Key"))
    return output
