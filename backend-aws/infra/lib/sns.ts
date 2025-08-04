import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as sns from "aws-cdk-lib/aws-sns";
import * as ssm from "aws-cdk-lib/aws-ssm";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { SqsStack } from "./sqs";

interface SnsStackProps extends cdk.StackProps {
    sqsStack: SqsStack;
}

export class SnsStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: SnsStackProps) {
        super(scope, id, props);

        const { sqsStack } = props;

        const fileIngestionTopic = new sns.Topic(this, "file-ingestion", {
            topicName: "file-ingestion",
            displayName: "File Ingestion Notifications",
        });

        // Subscribe file-ingestion topic to file-ingestion-request queue
        new sns.Subscription(this, "file-ingestion-to-request-queue", {
            topic: fileIngestionTopic,
            endpoint: sqsStack.fileIngestionRequestQueue.queueArn,
            protocol: sns.SubscriptionProtocol.SQS,
        });

        new ssm.StringParameter(this, "file-ingestion-topic-arn", { 
            parameterName: "/file-ingestion/sns/topic-arn",
            stringValue: fileIngestionTopic.topicArn,
            description: "ARN of the File Ingestion SNS Topic",
            tier: ssm.ParameterTier.STANDARD,
        });

        new cdk.CfnOutput(this, "file-ingestion-topic-arn-output", {
            value: fileIngestionTopic.topicArn,
            description: "The ARN of the File Ingestion SNS Topic",
        });

        const llmChat = new sns.Topic(this, "llm-chat", {
            topicName: "llm-chat",
            displayName: "LLM Chat Notifications",
        });

        // Subscribe llm-chat topic to llm-chat-request queue
        new sns.Subscription(this, "llm-chat-to-request-queue", {
            topic: llmChat,
            endpoint: sqsStack.llmChatRequestQueue.queueArn,
            protocol: sns.SubscriptionProtocol.SQS,
        });

        new ssm.StringParameter(this, "llm-chat-topic-arn", { 
            parameterName: "/llm-chat/sns/topic-arn",
            stringValue: llmChat.topicArn,
            description: "ARN of the LLM Chat SNS Topic",
            tier: ssm.ParameterTier.STANDARD,
        });

        new cdk.CfnOutput(this, "llm-chat-topic-arn-output", {
            value: llmChat.topicArn,
            description: "The ARN of the LLM Chat SNS Topic",
        });
    }
}
