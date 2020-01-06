import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("marketCatalogueScraper")
logger.setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s | %(filename)s | %(module)s",
    level=logging.INFO,
)


# Upload a new file
def upload_to_s3(local_path, s3_path, bucket):
    """Upload a file to an S3 bucket
    :param local_path: File to upload
    :param bucket: The name of the S3 bucket
    :param s3_path: Path inside S3 to store the data
    """
    # Upload the file
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(local_path, bucket, s3_path)
    except ClientError as e:
        logging.error(e)
        print(e)


def download_from_s3(local_path, s3_path, bucket):
    """Download a file from an S3 bucket
        :param local_path: Path to save the file
        :param bucket: The name of the S3 bucket
        :param s3_path: S3 path
        """
    s3_client = boto3.client("s3")
    try:
        s3_client.download_file(bucket, s3_path, local_path)
    except ClientError as e:
        logging.error(e)
        print(e)


def s3_dir_exists(s3_path, bucket):
    """Check if a file exists in a user-supplied S3 directory
    :param s3_path: The path to search for the file
    :param bucket: The name of the S3 bucket
    """

    s3_client = boto3.resource("s3")
    try:
        s3_client.Object(bucket, s3_path).load()
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
def list_files(prefix, bucket):
    """List files in specific S3 URL
        :param prefix: The path to search for the file
        :param bucket: The name of the S3 bucket
        """
    s3_client = boto3.client("s3")
    try:
        response = s3_client.list_objects(Bucket=bucket, Prefix=prefix)
        output = []
        for content in response.get("Contents", []):
            output.append(content.get("Key"))
        return output
    except ClientError as e:
        logging.error(e)
        print(e)
