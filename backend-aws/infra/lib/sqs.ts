import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as sqs from "aws-cdk-lib/aws-sqs";
import * as ssm from "aws-cdk-lib/aws-ssm";

export class SqsStack extends cdk.Stack {
    public readonly fileIngestionRequestQueue: sqs.Queue;
    public readonly fileIngestionReplyQueue: sqs.Queue;
    public readonly llmChatRequestQueue: sqs.Queue;
    public readonly llmChatResponseQueue: sqs.Queue;
    public readonly fileIngestionRequestDLQ: sqs.Queue;
    public readonly fileIngestionReplyDLQ: sqs.Queue;
    public readonly llmChatRequestDLQ: sqs.Queue;
    public readonly llmChatResponseDLQ: sqs.Queue;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Create Dead Letter Queues
        this.fileIngestionRequestDLQ = new sqs.Queue(this, "file-ingestion-request-dlq", {
            queueName: "file-ingestion-request-dlq",
            encryption: sqs.QueueEncryption.SQS_MANAGED,
            retentionPeriod: cdk.Duration.days(14),
        });

        this.fileIngestionReplyDLQ = new sqs.Queue(this, "file-ingestion-reply-dlq", {
            queueName: "file-ingestion-reply-dlq",
            encryption: sqs.QueueEncryption.SQS_MANAGED,
            retentionPeriod: cdk.Duration.days(14),
        });

        this.llmChatRequestDLQ = new sqs.Queue(this, "llm-chat-request-dlq", {
            queueName: "llm-chat-request-dlq",
            encryption: sqs.QueueEncryption.SQS_MANAGED,
            retentionPeriod: cdk.Duration.days(14),
        });

        this.llmChatResponseDLQ = new sqs.Queue(this, "llm-chat-response-dlq", {
            queueName: "llm-chat-response-dlq",
            encryption: sqs.QueueEncryption.SQS_MANAGED,
            retentionPeriod: cdk.Duration.days(14),
        });

        // Create main queues with Dead Letter Queue configuration
        this.fileIngestionRequestQueue = new sqs.Queue(this, "file-ingestion-request-queue", {
            queueName: "file-ingestion-request-queue",
            visibilityTimeout: cdk.Duration.seconds(120),
            encryption: sqs.QueueEncryption.SQS_MANAGED,
            deadLetterQueue: {
                queue: this.fileIngestionRequestDLQ,
                maxReceiveCount: 1,
            },
        });

        new ssm.StringParameter(this, "file-ingestion-request-queue-url-parameter", {
            parameterName: "/file-ingestion-request/sqs/queue-url",
            stringValue: this.fileIngestionRequestQueue.queueUrl,
            description: "URL of the File Ingestion Request SQS Queue",
            tier: ssm.ParameterTier.STANDARD,
        });

        new cdk.CfnOutput(this, "file-ingestion-request-queue-url-output", {
            value: this.fileIngestionRequestQueue.queueUrl,
            description: "The URL of the File Ingestion Request SQS Queue",
        });

        new cdk.CfnOutput(this, "file-ingestion-request-dlq-url-output", {
            value: this.fileIngestionRequestDLQ.queueUrl,
            description: "The URL of the File Ingestion Request Dead Letter Queue",
        });

        this.fileIngestionReplyQueue = new sqs.Queue(this, "file-ingestion-reply-queue", {
            queueName: "file-ingestion-reply-queue",
            visibilityTimeout: cdk.Duration.seconds(120),
            encryption: sqs.QueueEncryption.SQS_MANAGED,
            deadLetterQueue: {
                queue: this.fileIngestionReplyDLQ,
                maxReceiveCount: 1,
            },
        });

        new ssm.StringParameter(this, "file-ingestion-reply-queue-url-parameter", {
            parameterName: "/file-ingestion-reply/sqs/queue-url",
            stringValue: this.fileIngestionReplyQueue.queueUrl,
            description: "URL of the File Ingestion Reply SQS Queue",
            tier: ssm.ParameterTier.STANDARD,
        });

        new cdk.CfnOutput(this, "file-ingestion-reply-queue-url-output", {
            value: this.fileIngestionReplyQueue.queueUrl,
            description: "The URL of the File Ingestion Reply SQS Queue",
        });

        new cdk.CfnOutput(this, "file-ingestion-reply-dlq-url-output", {
            value: this.fileIngestionReplyDLQ.queueUrl,
            description: "The URL of the File Ingestion Reply Dead Letter Queue",
        });

        this.llmChatRequestQueue = new sqs.Queue(this, "llm-chat-request-queue", {
            queueName: "llm-chat-request-queue",
            visibilityTimeout: cdk.Duration.seconds(120),
            encryption: sqs.QueueEncryption.SQS_MANAGED,
            deadLetterQueue: {
                queue: this.llmChatRequestDLQ,
                maxReceiveCount: 1,
            },
        });

        new ssm.StringParameter(this, "llm-chat-request-queue-url-parameter", {
            parameterName: "/llm-chat-request/sqs/queue-url",
            stringValue: this.llmChatRequestQueue.queueUrl,
            description: "URL of the LLM Chat Request SQS Queue",
            tier: ssm.ParameterTier.STANDARD,
        });

        new cdk.CfnOutput(this, "llm-chat-request-queue-url-output", {
            value: this.llmChatRequestQueue.queueUrl,
            description: "The URL of the LLM Chat Request SQS Queue",
        });

        new cdk.CfnOutput(this, "llm-chat-request-dlq-url-output", {
            value: this.llmChatRequestDLQ.queueUrl,
            description: "The URL of the LLM Chat Request Dead Letter Queue",
        });

        
        this.llmChatResponseQueue = new sqs.Queue(this, "llm-chat-response-queue", {
            queueName: "llm-chat-response-queue",
            visibilityTimeout: cdk.Duration.seconds(120),
            encryption: sqs.QueueEncryption.SQS_MANAGED,
            deadLetterQueue: {
                queue: this.llmChatResponseDLQ,
                maxReceiveCount: 1,
            },
        });

        new ssm.StringParameter(this, "llm-chat-response-queue-url-parameter", {
            parameterName: "/llm-chat-response/sqs/queue-url",
            stringValue: this.llmChatResponseQueue.queueUrl,
            description: "URL of the LLM Chat Response SQS Queue",
            tier: ssm.ParameterTier.STANDARD,
        });

        new cdk.CfnOutput(this, "llm-chat-response-queue-url-output", {
            value: this.llmChatResponseQueue.queueUrl,
            description: "The URL of the LLM Chat Response SQS Queue",
        });

        new cdk.CfnOutput(this, "llm-chat-response-dlq-url-output", {
            value: this.llmChatResponseDLQ.queueUrl,
            description: "The URL of the LLM Chat Response Dead Letter Queue",
        });
    }
}
