from typing import Sequence
from constructs import Construct
from aws_cdk.aws_lambda import Function, Runtime, Code, LayerVersion
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk import Duration
from os import path

"""
Bug or wrong usage..
"""


class LambdaFunction(Function):
    def __init__(
        self,
        scope: Construct,
        id: str,
        handler: str,
        policies: Sequence[PolicyStatement],
    ) -> None:
        super().__init__(
            scope,
            id,
            handler=handler,
            runtime=Runtime.PYTHON_3_8,
            code=Code.from_asset(path=path.join(path.dirname(__file__), "../function")),
            memory_size=512,
            timeout=Duration.minutes(5),
            # Lambda Layer for Pillow lib
            # https://api.klayers.cloud//api/v2/p3.8/layers/latest/eu-central-1/html
            layers=[
                LayerVersion.from_layer_version_arn(
                    self,
                    f"{id}PillowPythonLayer",
                    "arn:aws:lambda:eu-central-1:770693421928:layer:Klayers-p38-Pillow:1",
                )
            ],
            initial_policy=policies,
        )
