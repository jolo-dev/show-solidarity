from aws_cdk import CfnOutput
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
            **kwargs,
        )

        CfnOutput(self, "BucketName", value=self.bucket_name)
        CfnOutput(self, "BucketArn", value=self.bucket_arn)
