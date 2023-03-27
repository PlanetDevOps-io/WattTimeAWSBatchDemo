import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as lambdaPy from '@aws-cdk/aws-lambda-python-alpha';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import { Construct } from 'constructs';

export class WattimeawsbatchStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create the WattTime Lambda
    const wattimeLambda = new lambdaPy.PythonFunction(this, 'MyFunction', {
      entry: 'lambda',
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'handler',
    });

    // Set up the EventBridge rule to trigger the Lambda function every 5 minutes
    const rule = new events.Rule(this, 'WattimeLambdaRule', {
      schedule: events.Schedule.rate(cdk.Duration.minutes(5)),
    });
    rule.addTarget(new targets.LambdaFunction(wattimeLambda));

    // Create an SNS topic
    const snsTopic = new sns.Topic(this, 'WattimeSNSTopic');

    // Add an email subscription to the topic
    snsTopic.addSubscription(
      new subscriptions.EmailSubscription('edwin@planetdevops.io')
    );
    // Grant the Lambda function permission to read the specified parameters
    wattimeLambda.addToRolePolicy(new cdk.aws_iam.PolicyStatement({
      actions: ['ssm:GetParametersByPath'],
      resources: ['arn:aws:ssm:*:*:parameter/wattime/*'],
    }));

    // Grant the Lambda function permission to publish to the SNS topic
    snsTopic.grantPublish(wattimeLambda);

    // Add the SNS topic ARN as an environment variable for the Lambda function
    wattimeLambda.addEnvironment('SNS_TOPIC_ARN', snsTopic.topicArn);
  }
}
