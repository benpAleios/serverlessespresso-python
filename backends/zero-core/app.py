#!/usr/bin/env python3

import aws_cdk as cdk

from zero_core.zero_core_stack import ZeroCoreStack


app = cdk.App()
ZeroCoreStack(app, "zero-core")

app.synth()
