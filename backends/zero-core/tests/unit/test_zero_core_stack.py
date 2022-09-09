import aws_cdk as core
import aws_cdk.assertions as assertions
from zero_core.zero_core_stack import ZeroCoreStack


def test_sqs_queue_created():
    app = core.App()
    stack = ZeroCoreStack(app, "zero-core")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })


def test_sns_topic_created():
    app = core.App()
    stack = ZeroCoreStack(app, "zero-core")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::SNS::Topic", 1)
