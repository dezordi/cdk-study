from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_s3_deployment as s3_deploy,
    aws_apigateway as apigw,
    aws_cognito as cognito,
)


class BuildingModernAppsCourseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dragon_app_path = self.node.try_get_context("DragonAppPath")
        assert (
            dragon_app_path is not None
        ), "Specify a dragon_path_file through --context DragonAppPath=<path>."

        # start of https://aws-tc-largeobjects.s3.amazonaws.com/DEV-AWS-MO-BuildingRedux/exercise-1-exploring.html

        # create s3 bucket to store the application
        bucket_name = "dragon-application"

        application_bucket = s3.Bucket(
            self,
            "DragonApplicationBucket",
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
        )
        application_bucket.grant_public_access()

        # upload dragon app data files
        s3_deploy.BucketDeployment(
            self,
            "DeployDragonBasefile",
            sources=[s3_deploy.Source.asset(dragon_app_path)],
            destination_bucket=application_bucket,
        )

        # create smm parameters
        ssm.StringParameter(
            self,
            "DragonApplicationSSMParameter",
            parameter_name="dragon_data_bucket_name",
            string_value=bucket_name,
        )

        ssm.StringParameter(
            self,
            "DragonApplicationSSMFileParameter",
            parameter_name="dragon_data_file_name",
            string_value="dragon_stats_one.txt",
        )

        # start of https://aws-tc-largeobjects.s3.amazonaws.com/DEV-AWS-MO-BuildingRedux/exercise-2-api-mocks.html

        # create api
        dragons_api = apigw.RestApi(
            self,
            "DragonsAPPApi",
            rest_api_name="DragonsApp",
            deploy=True,
            deploy_options=apigw.StageOptions(stage_name="prod"),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                ],
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_origins=apigw.Cors.ALL_ORIGINS,
            ),
        )

        dragons_api_endpoint = dragons_api.root.add_resource("dragons")

        # cognito from https://aws-tc-largeobjects.s3.amazonaws.com/DEV-AWS-MO-BuildingRedux/exercise-3-cognito.html

        # Create Cognito User Pool
        user_pool = cognito.UserPool(
            self,
            "DragonsUserPool",
            user_pool_name="dragons-pool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True, phone=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True)
            ),
            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your email",
                email_body="Thanks for signing up! Your verification code is {####}",
            ),
        )

        # Create App Client
        user_pool.add_client(
            "dragons-webclient",
            generate_secret=True,
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(implicit_code_grant=True),
                scopes=[cognito.OAuthScope.OPENID],
                callback_urls=[
                    f"https://{bucket_name}.s3.amazonaws.com/dragonsapp/index.html"
                ],
            ),
        )

        user_pool.add_domain(
            "dragons-app-cog-domain",
            cognito_domain=dict(domain_prefix="dragons-app-cog"),
        )

        # Create cognito authorizer
        cognito_authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "DragonsAppCognitoAuthorizer",authorizer_name="cognito-authorizer",cognito_user_pools=[user_pool]
        )

        # create endpoints
        dragons_api_endpoint.add_method(
            "GET",
            apigw.MockIntegration(
                integration_responses=[apigw.IntegrationResponse(status_code="200")],
                passthrough_behavior=apigw.PassthroughBehavior.NEVER,
                request_templates={
                    "application/json": "{ 'statusCode': 200 }",
                },
            ),
            method_responses=[apigw.MethodResponse(status_code="200")],
            authorizer=cognito_authorizer,
        )

        dragon_model = dragons_api.add_model(
            "DragonResponseModel",
            content_type="application/json",
            model_name="Dragonmodel",
            schema=apigw.JsonSchema(
                schema=apigw.JsonSchemaVersion.DRAFT4,
                title="Dragon",
                type=apigw.JsonSchemaType.OBJECT,
                properties={
                    "dragonName": apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                    "description": apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                    "family": apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                    "city": apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                    "country": apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                    "state": apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                    "neighborhood": apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                    "reportingPhoneNumber": apigw.JsonSchema(
                        type=apigw.JsonSchemaType.STRING
                    ),
                    "confirmationRequired": apigw.JsonSchema(
                        type=apigw.JsonSchemaType.BOOLEAN
                    ),
                },
            ),
        )

        dragons_api_endpoint.add_method(
            "POST",
            apigw.MockIntegration(
                integration_responses=[apigw.IntegrationResponse(status_code="200")],
                passthrough_behavior=apigw.PassthroughBehavior.NEVER,
                request_templates={
                    "application/json": "{ 'statusCode': 200 }",
                },
            ),
            request_models={"application/json": dragon_model},
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                )
            ],
            request_validator_options=apigw.RequestValidatorOptions(
                request_validator_name="request-dragon-post",
                validate_request_body=True,
            ),
            authorizer=cognito_authorizer,
        )
