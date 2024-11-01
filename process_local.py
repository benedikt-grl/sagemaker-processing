import logging
import argparse
import json
import sys
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True, help="A local directory")
    parser.add_argument("--output_dir", type=str, help="Output directory", default="/opt/ml/processing/output")
    args = vars(parser.parse_args())

    print("sys.path")
    print(sys.path)
    print()

    print("os.getcwd()")
    print(os.getcwd())
    print()

    print("os.listdir()")
    print(os.listdir(os.getcwd()))
    print()

    from utils.files import find_files_recursively

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

    if not os.path.exists(args["input_dir"]):
        log.error(f"Given input directory {args['input_dir']} does not exist")
        exit(1)

    all_filepaths = list(find_files_recursively(args["input_dir"]))

    log.info(f"Number of images in {args['input_dir']}: {len(all_filepaths)}")

    # Store result to S3
    result = {
        "input_dir": args["input_dir"],
        "number_of_files": len(all_filepaths),
    }

    output_file = os.path.join(args["output_dir"], "file_counts.json")
    with open(output_file, "w") as f:
        json.dump(result, f, indent=4)
