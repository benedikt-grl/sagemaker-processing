import logging
from utils.s3 import find_all_keys
import argparse
import boto3
import json
import sys
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", type=str, required=True, help="S3 bucket name")
    parser.add_argument("--prefix", type=str, required=True, help="A folder inside an S3 bucket")
    parser.add_argument("--output_dir", type=str, help="Output directory", default="/opt/ml/processing/output")
    args = vars(parser.parse_args())

    # Configure logging
    log = logging.getLogger(os.path.basename(__file__))
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(os.path.join(args["output_dir"], "log.log"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    log.addHandler(stdout_handler)
    log.addHandler(file_handler)

    log.info("Input arguments:")
    log.info(json.dumps(args))

    log.debug(f"sys.path: [{', '.join(sys.path)}]")
    log.debug(f"pwd: {os.getcwd()}")

    s3 = boto3.client("s3")

    all_filepaths = find_all_keys(bucket=args["bucket"], prefix=args["prefix"], s3_client=s3)

    log.info(f"Number of filepaths in s3://{args['bucket']}/{args['prefix']}: {len(all_filepaths)}")

    # Store result to S3
    result = {
        "bucket": args["bucket"],
        "prefix": args["prefix"],
        "number_of_files": len(all_filepaths),
    }

    output_file = os.path.join(args["output_dir"], "file_counts.json")
    with open(output_file, "w") as f:
        json.dump(result, f, indent=4)
