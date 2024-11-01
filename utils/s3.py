import boto3
from botocore.exceptions import ClientError


def find_all_keys(bucket, prefix, s3_client, extensions=None):
    """
    Find all files (= keys) in a given S3 bucket and folder (= prefix).
    :param bucket: S3 bucket
    :param prefix: directory relative to bucket root
    :param s3_client: S3 client
    :param extensions: list of file extensions to match
    :return: list of all keys. These include the prefix.
    """

    if s3_client is None:
        s3_client = boto3.client("s3")

    all_keys = []

    # Initialize parameters for pagination
    continuation_token = None

    while True:
        # Set up the request parameters
        list_params = {
            "Bucket": bucket,
            "Prefix": prefix,
        }
        if continuation_token:
            list_params["ContinuationToken"] = continuation_token

        # Request to list objects
        response = s3_client.list_objects_v2(**list_params)

        # Add the keys to your list
        for obj in response.get("Contents", []):
            key = obj["Key"]

            # Filter by extension
            if extensions is None or any(key.endswith(ext) for ext in extensions):
                all_keys.append(key)

        # Check if there are more keys to fetch
        if response.get("IsTruncated"):  # If True, there are more keys to fetch
            continuation_token = response["NextContinuationToken"]
        else:
            break

    return all_keys


def key_exists(bucket, key, s3_client):
    try:
        # Try to fetch the object's metadata
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        # Check if the error is because the object doesn't exist
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            # If another error occurred, re-raise it
            raise
