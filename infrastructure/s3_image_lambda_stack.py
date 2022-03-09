from aws_cdk import App, Stack, CfnOutput
from constructs import Construct
from aws_cdk.aws_s3 import (
    Bucket,
    BucketEncryption,
    BlockPublicAccess,
    EventType,
    CorsRule,
    HttpMethods,
)
from aws_cdk.aws_s3_notifications import LambdaDestination
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import PolicyStatement
from os import path

# from dotenv import set_key


app = App()
stack = Stack(app, "ShowSolidarityStack")


class S3ImageLambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        bucket = Bucket(
            self,
            "show-solidarity-image-bucket",
            bucket_name=kwargs["bucket_name"],
            cors=[
                CorsRule(
                    allowed_methods=[
                        HttpMethods.PUT,
                        HttpMethods.POST,
                        HttpMethods.DELETE,
                    ],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    max_age=3000,
                )
            ],
            encryption=BucketEncryption.S3_MANAGED,
            block_public_access=BlockPublicAccess.BLOCK_ALL,
        )

        lambda_function = Function(
            self,
            "ImageLambda",
            runtime=Runtime.PYTHON_3_9,
            handler="lambda_function.handler",
            code=Code.from_asset(path=path.join(path.dirname(__file__), "../src")),
            initial_policy=[
                PolicyStatement(
                    actions=["s3:GetObject"],
                    resources=[bucket.bucket_arn, f"{bucket.bucket_arn}/*"],
                ),
                PolicyStatement(actions=["rekognition:DetectFaces"], resources=["*"]),
            ],
        )

        bucket.add_event_notification(
            EventType.OBJECT_CREATED, LambdaDestination(lambda_function)
        )

        CfnOutput(
            self,
            "BucketName",
            value=bucket.bucket_name,
            description="Destination Bucket of image upload",
        )
        CfnOutput(
            self,
            "LambdaFunctionName",
            value=lambda_function.function_name,
            description="Get triggered when new image added",
        )
