from aws_cdk import Stack
from constructs import Construct
from aws_cdk import (
    aws_apigateway as api,
    aws_lambda as lamb,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_notifications as s3_event,
    Duration,
)
from solidarity_bucket import SolidarityBucket
from state_machine import StepFunctions
from os import path


class ShowSolidarityStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        source_bucket = SolidarityBucket(
            self,
            "SourceSolidarityImageBucket",
        )

        result_bucket = SolidarityBucket(
            self,
            "ResultSolidarityImageBucket",
        )

        rekognition_function = lamb.Function(
            self,
            "RekognitionFunction",
            handler="rekognition.handler",
            initial_policy=[
                # iam.PolicyStatement(
                #     actions=["s3:GetObject", "s3:ListBucket"],
                #     resources=[
                #         source_bucket.bucket_arn,
                #         f"{source_bucket.bucket_arn}/*",
                #     ],
                # ),
                iam.PolicyStatement(
                    actions=["rekognition:DetectFaces"], resources=["*"]
                ),
            ],
            runtime=lamb.Runtime.PYTHON_3_8,
            code=lamb.Code.from_asset(
                path=path.join(path.dirname(__file__), "../function")
            ),
            memory_size=512,
            timeout=Duration.minutes(5),
            # Lambda Layer for Pillow lib
            # https://api.klayers.cloud//api/v2/p3.8/layers/latest/{Stack.of(self).region}/html
            layers=[
                lamb.LayerVersion.from_layer_version_arn(
                    self,
                    "RekognitionPillowPythonLayer",
                    f"arn:aws:lambda:{Stack.of(self).region}:770693421928:layer:Klayers-p38-Pillow:1",
                ),
                lamb.LayerVersion.from_layer_version_arn(
                    self,
                    "RekognitionNumpyPythonLayer",
                    f"arn:aws:lambda:{Stack.of(self).region}:770693421928:layer:Klayers-p38-numpy:1",
                ),
            ],
        )

        source_bucket.grant_read(rekognition_function)
        result_bucket.grant_put(rekognition_function)

        # Create trigger for Lambda function using suffix
        notification = s3_event.LambdaDestination(rekognition_function)
        notification.bind(self, source_bucket)
        # Add Create Event only for .jpg files
        source_bucket.add_object_created_notification(
            notification, s3.NotificationKeyFilter(suffix=".jpg")
        )
        # Add Create Event only for .png files
        source_bucket.add_object_created_notification(
            notification, s3.NotificationKeyFilter(suffix=".png")
        )
        # Add Create Event only for .jpeg files
        source_bucket.add_object_created_notification(
            notification, s3.NotificationKeyFilter(suffix=".jpeg")
        )

        sf = StepFunctions(
            self,
            "SolidarityStateMachine",
            source_bucket=source_bucket.bucket_arn,
            result_bucket=result_bucket.bucket_arn,
        )

        api.StepFunctionsRestApi(
            self,
            "StepFunctionRestApi",
            deploy=True,
            state_machine=sf.state_machine,
            deploy_options=api.StageOptions(
                logging_level=api.MethodLoggingLevel.INFO,
                caching_enabled=True,
                data_trace_enabled=True,
            ),
            default_cors_preflight_options=api.CorsOptions(
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                ],
                allow_methods=["OPTIONS", "POST"],
                allow_credentials=True,
                allow_origins=["http://localhost:3000"],
            ),
        )
