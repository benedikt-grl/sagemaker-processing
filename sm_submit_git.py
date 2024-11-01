from sagemaker.processing import FrameworkProcessor, ScriptProcessor
from sagemaker.sklearn import SKLearn
from sagemaker.pytorch import PyTorchProcessor
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker import Session


# BASE_DIR = "/home/bene/getreallabs/dev/sagemaker-processing"
ROLE = "arn:aws:iam::156287967409:role/sagemaker-admin"
IMAGE_URI = "992382717417.dkr.ecr.us-east-1.amazonaws.com/getreallabs:docker-images.sagemaker-pytorch-with-grl-parckages-image-clip.80"
BUCKET = "grl-ml-photorealistic-image-detection"

# Remote paths must begin with "/opt/ml/processing/".
remote_code_dir = "/opt/ml/processing/input/code"
remote_image_root = "/opt/ml/processing/data"
remote_models_dir = "/opt/ml/processing/models"
remote_output_dir = "/opt/ml/processing/output"

sagemaker_session = Session(default_bucket=BUCKET)

processor = PyTorchProcessor(
    image_uri=IMAGE_URI,
    framework_version=None,
    role=ROLE,
    instance_count=1,
    instance_type="ml.g5.4xlarge",
    sagemaker_session=sagemaker_session,
    code_location=f"s3://{BUCKET}/tmp", # S3 prefix where the code is uploaded to
    base_job_name="playground-sm-submit-git",
    command=["python"],
    env={
        "PYTHONPATH": remote_code_dir,
    },
)

# If we provide a source_dir, run() will copy the source directory to the code location.
# If we provide a git_config, run() will clone the git repository to /tmp and upload it from there to the code location.
processor.run(
    inputs=[
        ProcessingInput(source=f"s3://{BUCKET}", destination=remote_image_root),
    ],
    outputs=[ProcessingOutput(
        output_name="output",
        source=remote_output_dir,
        destination=f"s3://{BUCKET}/tmp/sagemaker-processing-playground")
    ],
    git_config={
        "repo": "git@github.com:benedikt-grl/sagemaker-processing.git",
        "branch": "main",
    },
    code="process_local.py",
    # source_dir=BASE_DIR,
    arguments=[
        "--input_dir", f"{remote_image_root}/juanma",
        "--output_dir", remote_output_dir,
    ],
)

print(f"Processing job submitted. Check output in s3://{BUCKET}/tmp/sagemaker-processing-playground")
