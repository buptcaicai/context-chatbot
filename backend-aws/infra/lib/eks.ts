import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as eks from "aws-cdk-lib/aws-eks";
import * as iam from "aws-cdk-lib/aws-iam";
import { KubectlLayer } from "@aws-cdk/lambda-layer-kubectl";

export class EksStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // 1. VPC with public and private subnets
        const vpc = new ec2.Vpc(this, "EksVpc", {
            maxAzs: 2,
            natGateways: 1,
            subnetConfiguration: [
                { name: "Public", subnetType: ec2.SubnetType.PUBLIC },
                { name: "Private", subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
            ],
        });

        // 2. EKS cluster with public access
        // @ts-ignore
        const cluster = new eks.Cluster(this, "EksCluster", {
            version: eks.KubernetesVersion.V1_32,
            vpc,
            endpointAccess: eks.EndpointAccess.PUBLIC,
            defaultCapacity: 1,
        });

        // 3. Managed node group in private subnets
        cluster.addNodegroupCapacity("DefaultNodeGroup", {
            desiredSize: 0,
            instanceTypes: [new ec2.InstanceType("t3a.small")],
            subnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
        });

        // 4. Create IAM policy for SSM access
        const ssmPolicy = new iam.ManagedPolicy(this, "SsmAccessPolicy", {
            managedPolicyName: "EKSAppSSMPolicy",
            statements: [
                new iam.PolicyStatement({
                    actions: ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"],
                    resources: [`arn:aws:ssm:${this.region}:${this.account}:parameter/*`],
                }),
            ],
        });

        // 5. Create IRSA-enabled Kubernetes service account
        const sa = cluster.addServiceAccount("AppServiceAccount", {
            name: "llm-chat-sa",
            namespace: "default",
        });

        // 6. Attach the policy to the IAM role associated with the service account
        ssmPolicy.attachToRole(sa.role);

        // 7. Outputs
        new cdk.CfnOutput(this, "ClusterName", {
            value: cluster.clusterName,
        });

        new cdk.CfnOutput(this, "ServiceAccountName", {
            value: sa.serviceAccountName,
        });

        new cdk.CfnOutput(this, "ServiceAccountRoleArn", {
            value: sa.role.roleArn,
        });

        new cdk.CfnOutput(this, "EksEndpoint", {
            value: cluster.clusterEndpoint,
        });

        new cdk.CfnOutput(this, "OidcIssuer", {
            value: cluster.openIdConnectProvider.openIdConnectProviderIssuer,
        });
    }
}
