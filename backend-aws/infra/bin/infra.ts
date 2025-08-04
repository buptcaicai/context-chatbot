#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { SnsStack } from "../lib/sns";
import { SqsStack } from "../lib/sqs";
import { EksStack } from "../lib/eks";

const app = new cdk.App();
const sqsStack = new SqsStack(app, "SqsStack");
new SnsStack(app, "SnsStack", { sqsStack });
new EksStack(app, "EksStack");
app.synth();
