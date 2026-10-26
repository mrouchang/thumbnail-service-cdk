import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { Function, Code, Runtime } from 'aws-cdk-lib/aws-lambda';
import { join } from 'path';
import { Effect, PolicyStatement } from 'aws-cdk-lib/aws-iam';

export class ThumbnailServiceCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const handler = new Function(this, 'handler-function-resizeImg', {
      runtime: Runtime.PYTHON_3_10,
      timeout: cdk.Duration.seconds(20),
      handler: 'app.s3_thumbnail_generator',
      code: Code.fromAsset(join(__dirname, '../lambdas')),
      environment: {
        REGION_NAME: "us-east-1",
        THUMBNAIL_SIZE: "128"
      }
    });

    const s3Bucket = new s3.Bucket(this, 'photo-bucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true
    });

    s3Bucket.grantReadWrite(handler);

    s3Bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED, new s3n.LambdaDestination(handler));
    
    handler.addToRolePolicy(
      new PolicyStatement({
        effect: Effect.ALLOW,
        actions: ['s3:*'],
        resources: ['*'] //'s3:PutObject, 's3:GetObject
      })
    )
  }
}
