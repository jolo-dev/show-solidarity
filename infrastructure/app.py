from aws_cdk import App, Environment
import os

from show_solidarity_stack import ShowSolidarityStack

app = App()

ShowSolidarityStack(
    app,
    "SolidarityImageStack",
    env=Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
