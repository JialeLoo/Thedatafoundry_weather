from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda as lambda_,
    aws_lambda_event_sources as  lambda_event_sources,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets
)
import os
import subprocess


class StagingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create an S3 bucket to store weather data
        weather_bucket = s3.Bucket(self, "WeatherAPIthedatafoundry")
        
        # Create a directory to store layer contents
        # layer_dir = os.path.join(os.getcwd(), 'layer')
        # os.makedirs(layer_dir, exist_ok=True)

        # Use pip to download 'requests' library and its dependencies into the directory
        # subprocess.check_call(['pip', 'install', '-t', layer_dir, 'requests'])

        # Create a Lambda Layer with 'requests' library
        # requests_layer = lambda_.LayerVersion(self, 'RequestsLayer',
        #     code=lambda_.Code.from_asset(layer_dir),
        #     compatible_runtimes=[lambda_.Runtime.PYTHON_3_10],
        #     description="Lambda Layer with 'requests' library"
        # )
        
        weather_lambda = lambda_.Function(self, 'WeatherAPI',
                                          handler='lambda_handler.lambda_handler',
                                          runtime=lambda_.Runtime.PYTHON_3_10,
                                          code=lambda_.Code.from_asset('lambda'),
                                          timeout=Duration.seconds(60),
                                          environment={
                                            "S3_BUCKET_NAME": weather_bucket.bucket_name,
                                            "base_url" : 'http://api.openweathermap.org/data/2.5/weather?',
                                            "api_key" : '477860eae3ff372319537e33d0503b9b',
                                            "city" : 'Melbourne,au'
                                          }
                                          )
        
        # Grant Lambda permission to write to the S3 bucket
        weather_bucket.grant_write(weather_lambda)
        
        # Grant permissions to Lambda function to use the Lambda layer
        # weather_lambda.add_to_role_policy(
        #     statement=iam.PolicyStatement(
        #         actions=['lambda:GetLayerVersion'],
        #         resources=[requests_layer.layer_version_arn]
        #     )
        # )
        
        # # Grant permissions to the CDK stack to make changes to EventBridge rules
        # weather_lambda.add_to_role_policy(
        #     statement=iam.PolicyStatement(
        #         actions=[
        #             'events:PutRule',
        #             'events:PutTargets',
        #             'events:RemoveTargets',
        #             'events:DeleteRule'
        #         ],
        #         resources=['*']  # Adjust the resource ARN as needed
        #     )
        # )


        # Create an EventBridge rule to trigger Lambda hourly
        rule = events.Rule(self, "WeatherDataRule",
            schedule=events.Schedule.cron(minute="0"),  # Trigger hourly
        )
        rule.add_target(targets.LambdaFunction(weather_lambda))
        
        
