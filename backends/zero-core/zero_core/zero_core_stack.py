from aws_cdk import (
    Stack,
    App,
    aws_ssm,
    aws_events,
    aws_iot,
    aws_lambda,
    aws_cognito,
    aws_logs,
    aws_iam,
    Duration,
    CfnOutput,

    )



class ZeroCoreStack(Stack):
    def __init__(self, app: App, id: str, **kwargs):
        super().__init__(app, id, **kwargs)

        ##########################################
        # Custom event bus                       #
        ##########################################
        
        ServerlesspressoEventBus = aws_events.CfnEventBus(
            self,
            "ServerlesspressoEventBus",
            name="ServerlesspressoEventBus"
            )
    
        CoreEventBusNameParameter = aws_ssm.CfnParameter(
            self,
            id="CoreEventBusNameParameter",
            name="!Sub /${AppName}/${Service}/eventbusname",
            description="Eventbus Name",
            type="String",
            value="!Ref ServerlesspressoEventBus"
        )
        
        CoreEventBusARNParameter = aws_ssm.CfnParameter(
            self,
            id="CoreEventBusARNParameter",
            name="!Sub /${AppName}/${Service}/eventbusarn",
            description="Eventbus ARN",
            type="String",
            value="!Ref ServerlesspressoEventBus"
        )
        
        ServerlesspressoRealtime = aws_iot.CfnThing(
            self,
            "serverlesspresso-realtime",
            attribute_payload={
                "attributes_key": "attributes"
            },
            thing_name="serverlesspresso-realtime"
        )
        
        IoTRealtimeParameter = aws_ssm.CfnParameter(
            self,
            id="IoTRealtimeParameter",
            name="!Sub /${AppName}/${Service}/realtime",
            description="IoTRealtime URL",
            type="String",
            value="IotEndpoint.IotEndpointAddress"
        )
        
        GetIoTEndpointFunction = aws_lambda.Function(
            self,
            id="GetIoTEndpointFunction",
            handler="GetIoTEndpoint.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_inline("./code/GetIoTEndpoint"),
            memory_size=128,
            timeout=Duration.seconds(3),
        )
        
        GetIoTEndpointLogGroup = aws_logs.CfnLogGroup(
            self,
            id="GetIoTEndpointLogGroup",
            log_group_name="/aws/lambda/${GetIoTEndpointFunction}",
        )
        
        '''
        IotEndpoint = custom_resources.AwsCustomResource(
            self,
            "IotEndpoint",
            function_name="GetIoTEndpointFunction",
            on_create=None,
            policy=custom_resources.AwsCustomResourcePolicy.from_sdk_calls(
                resources=custom_resources.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
        )'''
        
        DefineAuthChallenge = aws_lambda.Function(
            self,
            id="DefineAuthChallenge",
            handler="define-auth-challenge.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_inline("./code/cognito-triggers/")
        )
        
        CreateAuthChallenge = aws_lambda.Function(
            self,
            id="CreateAuthChallenge",
            handler="create-auth-challenge.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_inline("./code/cognito-triggers/")
            #need to add the permissions policy
        )
        
        VerifyAuthChallengeResponse = aws_lambda.Function(
            self,
            id="VerifyAuthChallengeResponse",
            handler="verify-auth-challenge-response.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_inline("./code/cognito-triggers/")
        )
        
        PreSignUp = aws_lambda.Function(
            self,
            id="PreSignUp",
            handler="pre-sign-up.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_inline("./code/cognito-triggers/")
        )
        
        UserPool = aws_cognito.CfnUserPool(
            self,
            id="UserPool",
            user_pool_name="UserPool",
            mfa_configuration="OFF",
            schema=[
                aws_cognito.CfnUserPool.SchemaAttributeProperty(
                    name="phone_number",
                    attribute_data_type="String",
                    mutable=False,
                    required=True,
                )
            ],
            policies=aws_cognito.CfnUserPool.PoliciesProperty(
                password_policy=aws_cognito.CfnUserPool.PasswordPolicyProperty(
                    minimum_length=6,
                    require_lowercase=False,
                    require_numbers=False,
                    require_symbols=False,
                    require_uppercase=False,
                )
            ),
            username_attributes=["phone_number"],
            lambda_config=aws_cognito.CfnUserPool.LambdaConfigProperty(
                create_auth_challenge="!GetAtt CreateAuthChallenge.Arn",
                define_auth_challenge="!GetAtt DefineAuthChallenge.Arn",
                pre_sign_up="!GetAtt PreSignUp.Arn",
                verify_auth_challenge_response="!GetAtt VerifyAuthChallengeResponse.Arn"
                ),
            )
            
        DefineAuthChallengeInvocationPermission = aws_lambda.CfnPermission(
            self,
            id="DefineAuthChallengeInvocationPermission",
            function_name="!GetAtt DefineAuthChallenge.Arn",
            action="lambda:InvokeFunction",
            principal="cognito-idp.amazonaws.com",
            source_arn="!GetAtt UserPool.Arn"
        )
        
        CreateAuthChallengeInvocationPermission = aws_lambda.CfnPermission(
            self,
            id="CreateAuthChallengeInvocationPermission",
            function_name="!GetAtt CreateAuthChallenge.Arn",
            action="lambda:InvokeFunction",
            principal="cognito-idp.amazonaws.com",
            source_arn="!GetAtt UserPool.Arn"
        )
        
        VerifyAuthChallengeResponseInvocationPermission = aws_lambda.CfnPermission(
            self,
            id="VerifyAuthChallengeResponseInvocationPermission",
            function_name="!GetAtt VerifyAuthChallengeResponse.Arn",
            action="lambda:InvokeFunction",
            principal="cognito-idp.amazonaws.com",
            source_arn="!GetAtt UserPool.Arn",
        )
        
        PreSignUpInvocationPermission = aws_lambda.CfnPermission(
            self,
            id="PreSignUpInvocationPermission",
            function_name="!GetAtt PreSignUp.Arn",
            action="lambda:InvokeFunction",
            principal="cognito-idp.amazonaws.com",
            source_arn="!GetAtt UserPool.Arn",
        )
        
        UserPoolParameter = aws_ssm.CfnParameter(
            self,
            id="UserPoolParameter",
            name="!Sub /${AppName}/${Service}/userpool",
            description="UserPool ID",
            type="String",
            value="!Ref UserPool",
        )
        
        UserPoolClient = aws_cognito.CfnUserPoolClient(
            self,
            id="UserPoolClient",
            client_name="ServerlesspressoUserPoolClient",
            generate_secret=False,
            user_pool_id="!Ref UserPool",
            explicit_auth_flows=["CUSTOM_AUTH_FLOW_ONLY"],   
        )
        
        UserPoolClientParameter = aws_ssm.CfnParameter(
            self,
            id="UserPoolClientParameter",
            name="!Sub /${AppName}/${Service}/userpoolclient",
            description="UserPool Client",
            type="String",
            value="!Ref UserPoolClient"
        )
        
        IdentityPool = aws_cognito.CfnIdentityPool(
            self,
            id="IdentityPool",
            identity_pool_name="ServerlesspressoIdentityPool",
            allow_unauthenticated_identities=True,
            cognito_identity_providers=[aws_cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                client_id="!Ref UserPoolClient",
                provider_name="!GetAtt UserPool.ProviderName"
            )]
        )
        
        
        CognitoUnAuthorizedRole = aws_iam.CfnRole(
            self,
            id="CognitoUnAuthorizedRole",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement":[
                    {
                        "Principal":{
                            "Federated":"cognito-identity.amazonaws.com"
                        },
                        "Effect":"Allow",
                        "Action":[
                            "sts:AssumeRoleWithWebIdentity"
                        ],
                        "Condition":{
                            "StringEquals":{
                                "cognito-identity.amazonaws.com:aud": "!Ref IdentityPool"
                            },
                            "ForAnyValue:StringLike":{
                                "cognito-identity.amazonaws.com:amr": "unauthenticated"
                            }
                        }
                    }
                ]
            },
            policies=[
                aws_iam.CfnRole.PolicyProperty(
                    policy_name="CognitoUnauthorizedPolicy",
                    policy_document={
                        "Version":"2012-10-17",
                        "Statement":[
                            {
                                "Effect":"Allow",
                                "Action":[
                                    "cognito-sync:*"
                                ],
                                "Resource":'!Join [ "", [ "arn:aws:cognito-sync:", !Ref "AWS::Region", ":", !Ref "AWS::AccountId", ":identitypool/", !Ref IdentityPool] ]'
                            },
                            {
                                "Effect":"Allow",
                                "Action":[
                                    "iot:Connect"
                                ],
                                "Resource":'!Join [ "", [ "arn:aws:iot:", !Ref "AWS::Region", ":", !Ref "AWS::AccountId", ":client/serverlesspresso-*" ] ]'
                            },
                            {
                                "Effect":"Allow",
                                "Action":[
                                    "iot:Subscribe"
                                ],
                                "Resource":"*"
                            },
                            {
                                "Effect":"Allow",
                                "Action":[
                                    "iot:Receive"
                                ],
                                "Resource":'!Join [ "", [ "arn:aws:iot:", !Ref "AWS::Region", ":", !Ref "AWS::AccountId", ":topic/*" ] ]'
                            }
                        ]
                    }
                )
            ]
        )
        
        
        
        CognitoAuthorizedRole = aws_iam.CfnRole(
            self,
            id="CognitoAuthorizedRole",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement":[
                    {
                        "Principal":{
                            "Federated":"cognito-identity.amazonaws.com"
                        },
                        "Effect":"Allow",
                        "Action":[
                            "sts:AssumeRoleWithWebIdentity"
                        ],
                        "Condition":{
                            "StringEquals":{
                                "cognito-identity.amazonaws.com:aud": "!Ref IdentityPool"
                            },
                            "ForAnyValue:StringLike":{
                                "cognito-identity.amazonaws.com:amr": "authenticated"
                            }
                        }
                    }
                ]
            },
            policies=[
                aws_iam.CfnRole.PolicyProperty(
                    policy_name="CognitoAuthorizedPolicy",
                    policy_document={
                        "Version":"2012-10-17",
                        "Statement":[
                            {
                                "Effect":"Allow",
                                "Action":[
                                    "cognito-sync:*"
                                ],
                                "Resource":'!Join [ "", [ "arn:aws:cognito-sync:", !Ref "AWS::Region", ":", !Ref "AWS::AccountId", ":identitypool/", !Ref IdentityPool] ]'
                            },
                            {
                                "Effect":"Allow",
                                "Action":[
                                    "iot:Connect"
                                ],
                                "Resource":'!Join [ "", [ "arn:aws:iot:", !Ref "AWS::Region", ":", !Ref "AWS::AccountId", ":client/serverlesspresso-*" ] ]'
                            },
                            {
                                "Effect":"Allow",
                                "Action":[
                                    "iot:Subscribe"
                                ],
                                "Resource":"*"
                            },
                            {
                                "Effect":"Allow",
                                "Action":[
                                    "iot:Receive"
                                ],
                                "Resource":'!Join [ "", [ "arn:aws:iot:", !Ref "AWS::Region", ":", !Ref "AWS::AccountId", ":topic/*" ] ]'
                            }
                        ]
                    }
                )
            ]
        )
        
        IdentityPoolRoleMapping = aws_cognito.CfnIdentityPoolRoleAttachment(
            self,
            id="IdentityPoolRoleMapping",
            identity_pool_id="IdentityPoolRoleMapping",
            roles={
                "authenticated":"!GetAtt CognitoAuthorizedRole.Arn",
                "unauthenticated":"!GetAtt CognitoUnAuthorizedRole.Arn"
            }
        )
        
        CfnOutput(
            self,
            id="CoreEventBusNameOutput",
            description="CoreEventBus Name",
            value="!Ref ServerlesspressoEventBus"
        )
        
        CfnOutput(
            self,
            id="CoreEventBusARNOutput",
            description="CoreEventBus Arn",
            value="!GetAtt ServerlesspressoEventBus.Arn"
        )
        
        CfnOutput(
            self,
            id="UserPoolIDOutput",
            description="UserPool ID",
            value="!Ref UserPool"
        )
        
        CfnOutput(
            self,
            id="UserPoolClientOutput",
            description="UserPool Client",
            value="!Ref UserPoolClient"
        )
        
        CfnOutput(
            self,
            id="IoTRealtimeNameOutput",
            description="IoTRealtime Name",
            value="!Ref ServerlesspressoRealtime"
        )
        
        CfnOutput(
            self,
            id="IotEndpointAddressOutput",
            description="IoTRealtime Address",
            value="!GetAtt IotEndpoint.IotEndpointAddress",
            export_name='!Sub "${AWS::StackName}-IotEndpointAddress"'
        )