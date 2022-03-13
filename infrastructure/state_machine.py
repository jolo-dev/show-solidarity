from aws_cdk.aws_stepfunctions import StateMachine, Wait, WaitTime, LogLevel
from aws_cdk.aws_stepfunctions_tasks import LambdaInvoke
from constructs import Construct
from aws_cdk.aws_iam import PolicyStatement
from lambda_function import LambdaFunction
from aws_cdk.aws_logs import LogGroup


class StepFunctions(Construct):
    def __init__(
        self, scope: Construct, id: str, source_bucket: str, result_bucket: str
    ) -> None:
        super().__init__(scope, id)

        put_source_function = LambdaFunction(
            self,
            "PutToSource",
            handler="put_object.handler",
            policies=[
                PolicyStatement(
                    actions=["s3:PutObject"],
                    resources=[source_bucket, f"{source_bucket}/*"],
                ),
            ],
        )

        put_source = LambdaInvoke(
            self,
            "PutObjectInSourceBucket",
            lambda_function=put_source_function,
            input_path="$.input",
            output_path="$.payload",
        )

        waitX = Wait(self, "WaitXSeconds", time=WaitTime.seconds_path("$.waitSeconds"))

        rekognition_function = LambdaFunction(
            self,
            "Rekognition",
            handler="rekognition.handler",
            policies=[
                PolicyStatement(
                    actions=["s3:GetObject"],
                    resources=[source_bucket, f"{source_bucket}/*"],
                ),
                PolicyStatement(actions=["rekognition:DetectFaces"], resources=["*"]),
            ],
        )

        rekognition = LambdaInvoke(
            self,
            "Rekognition",
            lambda_function=rekognition_function,
            input_path="$.input",
            output_path="$.payload",
        )

        put_result_function = LambdaFunction(
            self,
            "PutToResult",
            handler="put_object.handler",
            policies=[
                PolicyStatement(
                    actions=["s3:PutObject"],
                    resources=[result_bucket, f"{result_bucket}/*"],
                ),
            ],
        )

        put_result = LambdaInvoke(
            self,
            "PutToResult",
            lambda_function=put_result_function,
            input_path="$.input",
            output_path="$.result",
        )

        logGroup = LogGroup(
            self, "SolidarityStepFunctions", log_group_name="SolidarityStepFunctions"
        )
        definition = put_source.next(waitX).next(rekognition).next(put_result)
        StateMachine(
            self,
            "SolidarityStatemachine",
            definition=definition,
            tracingEnabled=True,
            logs={"destination": logGroup, "level": LogLevel.ALL},
        )
