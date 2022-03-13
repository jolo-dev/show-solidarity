from aws_cdk.aws_stepfunctions import (
    StateMachine,
    Wait,
    WaitTime,
    LogLevel,
    StateMachineType,
)
from aws_cdk.aws_stepfunctions_tasks import LambdaInvoke
from constructs import Construct
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.aws_logs import LogGroup
from aws_cdk.aws_lambda import Function, Runtime, Code, LayerVersion
from aws_cdk import Duration
from os import path


class StepFunctions(Construct):

    state_machine: StateMachine

    def __init__(
        self, scope: Construct, id: str, source_bucket: str, result_bucket: str
    ) -> None:
        super().__init__(scope, id)

        put_source_function = Function(
            self,
            "PutToSourceFunction",
            handler="put_object.handler",
            initial_policy=[
                PolicyStatement(
                    actions=["s3:PutObject"],
                    resources=[source_bucket, f"{source_bucket}/*"],
                ),
            ],
            runtime=Runtime.PYTHON_3_8,
            code=Code.from_asset(path=path.join(path.dirname(__file__), "../function")),
            memory_size=512,
            timeout=Duration.minutes(5),
            # Lambda Layer for Pillow lib
            # https://api.klayers.cloud//api/v2/p3.8/layers/latest/eu-central-1/html
            layers=[
                LayerVersion.from_layer_version_arn(
                    self,
                    "PutToSourceFunctionPillowPythonLayer",
                    "arn:aws:lambda:eu-central-1:770693421928:layer:Klayers-p38-Pillow:1",
                )
            ],
        )

        put_source = LambdaInvoke(
            self,
            "PutToSource",
            lambda_function=put_source_function,
            input_path="$.body",
            output_path="$.payload",
        )

        waitX = Wait(self, "WaitXSeconds", time=WaitTime.seconds_path("$.waitSeconds"))

        rekognition_function = Function(
            self,
            "RekognitionFunction",
            handler="rekognition.handler",
            initial_policy=[
                PolicyStatement(
                    actions=["s3:GetObject"],
                    resources=[source_bucket, f"{source_bucket}/*"],
                ),
                PolicyStatement(actions=["rekognition:DetectFaces"], resources=["*"]),
            ],
            runtime=Runtime.PYTHON_3_8,
            code=Code.from_asset(path=path.join(path.dirname(__file__), "../function")),
            memory_size=512,
            timeout=Duration.minutes(5),
            # Lambda Layer for Pillow lib
            # https://api.klayers.cloud//api/v2/p3.8/layers/latest/eu-central-1/html
            layers=[
                LayerVersion.from_layer_version_arn(
                    self,
                    "RekognitionPillowPythonLayer",
                    "arn:aws:lambda:eu-central-1:770693421928:layer:Klayers-p38-Pillow:1",
                )
            ],
        )

        rekognition = LambdaInvoke(
            self,
            "Rekognition",
            lambda_function=rekognition_function,
            input_path="$.payload",
            output_path="$.output",
        )

        put_result_function = Function(
            self,
            "PutToResultFunction",
            handler="put_object.handler",
            initial_policy=[
                PolicyStatement(
                    actions=["s3:PutObject"],
                    resources=[result_bucket, f"{result_bucket}/*"],
                ),
            ],
            runtime=Runtime.PYTHON_3_8,
            code=Code.from_asset(path=path.join(path.dirname(__file__), "../function")),
            memory_size=512,
            timeout=Duration.minutes(5),
            # Lambda Layer for Pillow lib
            # https://api.klayers.cloud//api/v2/p3.8/layers/latest/eu-central-1/html
            layers=[
                LayerVersion.from_layer_version_arn(
                    self,
                    "PutToResultPillowPythonLayer",
                    "arn:aws:lambda:eu-central-1:770693421928:layer:Klayers-p38-Pillow:1",
                )
            ],
        )

        put_result = LambdaInvoke(
            self,
            "PutToResult",
            lambda_function=put_result_function,
            input_path="$.output",
            output_path="$.result",
        )

        logGroup = LogGroup(
            self, "SolidarityStepFunctions", log_group_name="SolidarityStepFunctions"
        )
        definition = put_source.next(waitX).next(rekognition).next(put_result)

        self.state_machine = StateMachine(
            self,
            "SolidarityStatemachine",
            definition=definition,
            state_machine_type=StateMachineType.EXPRESS,
            tracing_enabled=True,
            logs={"destination": logGroup, "level": LogLevel.ALL},
        )
