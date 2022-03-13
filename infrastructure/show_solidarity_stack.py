from aws_cdk import Stack
from constructs import Construct
from aws_cdk.aws_apigateway import StepFunctionsRestApi
from solidarity_bucket import SolidarityBucket
from state_machine import StepFunctions


class ShowSolidarityStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        source_bucket = SolidarityBucket(
            self,
            "SourceSolidarityImageBucket",
            bucket_name=f'source-{kwargs["bucket_name"]}',
        )

        result_bucket = SolidarityBucket(
            self,
            "ResultSolidarityImageBucket",
            bucket_name=f'result-{kwargs["bucket_name"]}',
        )

        sf = StepFunctions(
            self,
            "SolidarityStateMachine",
            source_bucket=source_bucket.bucket_arn,
            result_bucket=result_bucket.bucket_arn,
        )

        StepFunctionsRestApi(
            self, "StepFunctionRestApi", deploy=True, state_machine=sf.state_machine
        )
