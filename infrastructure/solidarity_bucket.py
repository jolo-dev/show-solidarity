from aws_cdk import CfnOutput, RemovalPolicy
from aws_cdk.aws_s3 import (
    Bucket,
    BucketEncryption,
    BlockPublicAccess,
    CorsRule,
    HttpMethods,
)
from constructs import Construct


class SolidarityBucket(Bucket):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(
            scope,
            id,
            cors=[
                CorsRule(
                    allowed_methods=[
                        HttpMethods.GET,
                        HttpMethods.PUT,
                        HttpMethods.POST,
                    ],
                    allowed_origins=["http://localhost:3000"],
                    allowed_headers=[
                        "Authorization",
                        "x-amz-date",
                        "x-amz-content-sha256",
                        "content-type",
                    ],
                    max_age=3000,
                ),
                CorsRule(
                    allowed_methods=[
                        HttpMethods.GET,
                    ],
                    allowed_origins=["*"],
                    max_age=3000,
                ),
            ],
            encryption=BucketEncryption.S3_MANAGED,
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            **kwargs,
        )

        CfnOutput(self, "BucketName", value=self.bucket_name)
        CfnOutput(self, "BucketArn", value=self.bucket_arn)
