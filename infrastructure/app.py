from aws_cdk import App, Environment
import os

from show_solidarity_stack import ShowSolidarityStack

bucket_name = (
    os.getenv("BUCKET_NAME")
    if os.getenv("BUCKET_NAME") is not None
    else "show-solidarity"
)

app = App()

ShowSolidarityStack(
    app,
    "S3ImageLambdaStack",
    bucket_name=bucket_name,
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
