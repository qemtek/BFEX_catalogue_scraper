import logging

import boto3
from botocore.exceptions import ClientError

# Let's use Amazon S3
s3 = boto3.resource("s3")


# Upload a new file
def upload_to_s3(local_path, s3_path, bucket="betfair-exchange-qemtek"):
    """Upload a file to an S3 bucket

    :param local_path: File to upload
    :param bucket: Bucket to upload to
    :param s3_path: Path inside S3 to store the data
    """

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(local_path, bucket, s3_path)
    except ClientError as e:
        logging.error(e)
        print(e)


def download_from_s3(local_path, s3_path, bucket_name="betfair-exchange-qemtek"):
    """Download a file from an S3 bucket

        :param local_path: Path to save the file
        :param bucket: Bucket to upload to
        :param s3_path: S3 path
        """

    s3 = boto3.client("s3")
    s3.download_file(bucket_name, s3_path, local_path)
