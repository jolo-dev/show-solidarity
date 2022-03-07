from aws_cdk import App, Environment
import os

from s3_image_lambda_stack import S3ImageLambdaStack

bucket_name = (
    os.getenv("BUCKET_NAME")
    if os.getenv("BUCKET_NAME") is not None
    else "show-solidarity"
)

app = App()

S3ImageLambdaStack(
    app,
    "S3ImageLambdaStack",
    bucket_name=bucket_name,
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
