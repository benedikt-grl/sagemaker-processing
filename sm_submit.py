from sagemaker.processing import FrameworkProcessor, ScriptProcessor
from sagemaker.sklearn import SKLearn
from sagemaker.pytorch import PyTorchProcessor
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker import Session


BASE_DIR = "/home/bene/getreallabs/dev/sagemaker-processing"
ROLE = "arn:aws:iam::156287967409:role/sagemaker-admin"
IMAGE_URI = "992382717417.dkr.ecr.us-east-1.amazonaws.com/getreallabs:docker-images.sagemaker-pytorch-with-grl-parckages-image-clip.80"
BUCKET = "grl-ml-photorealistic-image-detection"


sagemaker_session = Session(default_bucket=BUCKET)


processor = PyTorchProcessor(
    image_uri=IMAGE_URI,
    framework_version=None,
    role=ROLE,
    instance_count=1,
    instance_type="ml.g5.4xlarge",
    sagemaker_session=sagemaker_session,
    code_location=f"s3://{BUCKET}/tmp", # S3 prefix where the code is uploaded to
    base_job_name="playground-v4",
    command=["python"],
    env={
        "PYTHONPATH": "/opt/ml/processing/input/code"
    },
)

# Remote paths must begin with "/opt/ml/processing/".
remote_code_dir = "/opt/ml/processing/input/code"
remote_image_root = "/opt/ml/processing/data"
remote_models_dir = "/opt/ml/processing/models"
remote_output_dir = "/opt/ml/processing/output"

model = "2024_10_07-ViT-H-14-378-quickgelu_dfn5b_clip_dnn_pos_weight_0.2"

processor.run(
    inputs=[
        ProcessingInput(source=f"s3://{BUCKET}", destination=remote_image_root),
        ProcessingInput(source=f"s3://{BUCKET}/experiments/nonphotorealistic-image-detection-dnn", destination=remote_models_dir),
    ],
    outputs=[ProcessingOutput(
        output_name="output",
        source=remote_output_dir,
        destination=f"s3://{BUCKET}/experiments/nonphotorealistic-image-detection-dnn/{model}/results")
    ],
    git_config={

    },
    code="process_local.py",
    source_dir=BASE_DIR,
    arguments=[
        "--input_dir", f"{remote_image_root}/juanma",
        "--output_dir", remote_output_dir,
    ],
)


# sklearn_processor = FrameworkProcessor(
#     estimator_cls=PyTorchProcessor,
#     instance_type="ml.m5.xlarge",
#     instance_count=1,
#     base_job_name="playground-v4",
#     sagemaker_session=sagemaker_session,
#     role=role,
#     env={
#         "PYTHONPATH": "/opt/ml/processing/input/code"
#     },
# )
#
# step_args = sklearn_processor.run(
#     outputs=[ProcessingOutput(
#         output_name="output",
#         source="/opt/ml/processing/output",
#         destination=f"s3://{bucket}/tmp/")
#     ],
#     code="utils/process.py",
#     source_dir=BASE_DIR,
#     arguments=[
#         "--bucket", bucket,
#         "--prefix", "juanma"
#     ],
# )

print(f"Processing job submitted. Check output in s3://{BUCKET}/tmp/")
