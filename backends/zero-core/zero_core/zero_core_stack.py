import string
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ssm,
    aws_events,
    aws_iot,
    )
import aws_cdk as cdk


class ZeroCoreStack(cdk.Stack):
    def __init__(self, app: cdk.App, id: str, **kwargs):
        super().__init__(app, id, **kwargs)

        ##########################################
        # Custom event bus                       #
        ##########################################
        
        ServerlesspressoEventBus = aws_events.EventBus(
            self,
            "bus",
            event_bus_name="Serverlesspresso"
            )
        
        CoreEventBusNameParameter = aws_ssm.StringParameter(
            self,
            id="CoreEventBusNameParameter",
            parameter_name="/eventbusname",
            description="Eventbus Name",
            type=aws_ssm.ParameterType.STRING,
            string_value="ServerlesspressoEventBus"
        )
        
        CoreEventBusARNParameter = aws_ssm.StringParameter(
            self,
            id="CoreEventBusARNParameter",
            parameter_name="/eventbusarn",
            description="Eventbus ARN",
            type=aws_ssm.ParameterType.STRING,
            string_value="ServerlesspressoEventBus.event_bus_arn"
        )
        
        ServerlesspressoRealtime = aws_iot.CfnThing(
            self,
            "serverlesspresso-realtime",
            attribute_payload={
                "attributes_key": "attributes"
            },
            thing_name="serverlesspresso-realtime"
        )
        
        IoTRealtimeParameter = aws_ssm.StringParameter(
            self,
            id="IoTRealtimeParameter",
            parameter_name="/realtime",
            description="IoTRealtime URL",
            type=aws_ssm.ParameterType.STRING,
            string_value="IotEndpoint.IotEndpointAddress"
        )