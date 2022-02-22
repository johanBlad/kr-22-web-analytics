# Welcome to your CDK TypeScript project!

This is a blank project for TypeScript development with CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

 * `npm run build`   compile typescript to js
 * `npm run watch`   watch for changes and compile
 * `npm run test`    perform the jest unit tests
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk synth`       emits the synthesized CloudFormation template

 * `aws cloudformation list-stacks |grep DataSinkStack`                                     ...
 * `aws cloudformation delete-stack --stack-name DataSinkStack`                             ...
 * `aws logs describe-log-groups |grep kr22`                                                ...
 * `aws logs delete-log-group --log-group-name "/aws/apigateway/kr22-web-event-kinesis"`    ...
 * `aws logs tail "/aws/lambda/kr-web-event-kinesis-processor" --follow --profile netlight` ...


## Invoke API

You can post events to the API by posting the following JS in your browser console, from https://klimatriksdagen.se

```
fetch("https://<api-id>.execute-api.eu-west-1.amazonaws.com/prod/events", {headers: {"content-type": "application/json"}, method: "POST", body: JSON.stringify({"event_type": "page_load", "from_url": window.location.href, "details": {}})})
```

## Utils

For SSO AWS login utility, integrated with CDK: https://github.com/victorskl/yawsso


