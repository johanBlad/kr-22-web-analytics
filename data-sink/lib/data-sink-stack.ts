import * as cdk from "@aws-cdk/core";
import * as glue from "@aws-cdk/aws-glue";
import * as s3 from "@aws-cdk/aws-s3";
import * as firehose from "@aws-cdk/aws-kinesisfirehose";
import * as iam from "@aws-cdk/aws-iam";
import * as lambda from "@aws-cdk/aws-lambda";
import * as logs from "@aws-cdk/aws-logs";
import * as apigateway from "@aws-cdk/aws-apigateway";
import dedent from "ts-dedent";

export class DataSinkStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, "Kr22WebEventBucket", {
      bucketName: "kr22.web.event-bucket",
      removalPolicy: cdk.RemovalPolicy.RETAIN, // TODO: Change this when going live
    });

    const database = new glue.Database(this, "Kr22WebEventDatabase", {
      databaseName: "kr22_web_event_database",
    });

    const cfnTable = new glue.CfnTable(this, "Kr22WebEventTable", {
      catalogId: this.account,
      databaseName: database.databaseName,
      tableInput: {
        description: "Tracking event data from KR22 web",
        name: "kr22_web_event_table",
        parameters: {
          "projection.datehour.type": "date",
          "projection.datehour.format": "yyyy-MM-dd",
          "projection.datehour.interval": "1",
          "projection.datehour.interval.unit": "DAYS",
          "projection.datehour.range": "2021-07-01/00,NOW",
          classification: "json",
          "projection.enabled": "true",
          "storage.location.template": bucket.s3UrlForObject(
            "events/result=success/${datehour}"
          ),
        },
        partitionKeys: [
          {
            name: "datehour",
            type: "string",
          },
        ],
        storageDescriptor: {
          bucketColumns: ["bucketColumns"],
          columns: [
            { name: "datehour ", type: "string" },
            { name: "name", type: "type" },
            { name: "name", type: "type" },
          ],
          inputFormat: "org.apache.hadoop.mapred.TextInputFormat",
          outputFormat:
            "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
          location: bucket.s3UrlForObject("/result=success/"),
          serdeInfo: {
            serializationLibrary: "org.openx.data.jsonserde.JsonSerDe",
          },
        },
      },
    });

    const firehoseRole = new iam.Role(this, "Kr22WebEventFirehoseRole", {
      assumedBy: new iam.ServicePrincipal("firehose.amazonaws.com"),
    });
    firehoseRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        "service-role/AWSGlueServiceRole"
      )
    );
    bucket.grantReadWrite(firehoseRole);

    // const processingLambda = new lambda.DockerImageFunction(this, "", {
    //   functionName: "kr-web-event-kinesis-processor",
    //   code: lambda.DockerImageCode.fromImageAsset("url.."),
    //   environment: {
    //     LOG_LEVEL: "level",
    //   },
    //   timeout: cdk.Duration.minutes(5),
    //   logRetention: logs.RetentionDays.ONE_WEEK,
    // });
    // processingLambda.grantInvoke(firehoseRole);

    const cfnDeliveryStream = new firehose.CfnDeliveryStream(
      this,
      "Kr22WebEventFirehose",
      {
        deliveryStreamName: "kr22_web_event_firehose",
        deliveryStreamType: "DirectPut",
        extendedS3DestinationConfiguration: {
          bucketArn: bucket.bucketArn,
          roleArn: firehoseRole.roleArn,
          bufferingHints: {
            intervalInSeconds: 900,
            sizeInMBs: 128,
          },
          // cloudWatchLoggingOptions: {
          //   enabled: false,
          //   logGroupName: "logGroupName",
          //   logStreamName: "logStreamName",
          // },
          errorOutputPrefix: "events/result=error/",
          prefix: "events/result=success/",
          // processingConfiguration: {
          //   enabled: true,
          //   processors: [
          //     {
          //       type: "Lambda",
          //       parameters: [
          //         {
          //           parameterName: "LambdaArn",
          //           parameterValue: processingLambda.functionArn,
          //         },
          //       ],
          //     },
          //   ],
          // },
        },
      }
    );

    //
    // API Gateway to connect to Kinesis
    //
    const apigatewayRole = new iam.Role(this, "ApiGatewayRole", {
      assumedBy: new iam.ServicePrincipal("apigateway.amazonaws.com"),
    });

    apigatewayRole.addToPolicy(
      new iam.PolicyStatement({
        resources: [cfnDeliveryStream.attrArn],
        actions: ["firehose:PutRecord", "firehose:PutRecordBatch"],
      })
    );

    const corsOptions = {
      allowOrigins: ["https://klimatriksdagen.se"],
      allowMethods: ["OPTIONS", "POST"],
      allowHeaders: ["content-type", "authorization"],
      maxAge: cdk.Duration.minutes(5),
    };

    const getCorsResponseParams = (
      corsOpts: apigateway.CorsOptions
    ): { [header: string]: string } => ({
      "method.response.header.Access-Control-Allow-Headers": `'${corsOpts.allowHeaders?.join()}'`,
      "method.response.header.Access-Control-Allow-Methods": `'${corsOpts.allowMethods?.join()}'`,
      "method.response.header.Access-Control-Max-Age": `'${corsOpts.maxAge?.toSeconds()}'`,
      "method.response.header.Access-Control-Allow-Origin": `'${corsOpts.allowOrigins[0]}'`,
    });

    const integrationResponseParams = getCorsResponseParams(corsOptions);
    const methodResponseParams = Object.keys(integrationResponseParams).reduce(
      (obj: { [k: string]: boolean }, k: string) => {
        obj[k] = true;
        return obj;
      },
      {}
    );

    // console.log({corsOptions});
    // console.log({integrationResponseParams});
    // console.log({methodResponseParams});
    

    const restApi = new apigateway.RestApi(this, "Kr22WebEventApi", {
      restApiName: "kr22_web_event_api",
      cloudWatchRole: false,
      deployOptions: {
        loggingLevel: apigateway.MethodLoggingLevel.ERROR,
        accessLogDestination: new apigateway.LogGroupLogDestination(
          new logs.LogGroup(this, "ApiGatewayLogGroup", {
            logGroupName: "/aws/apigateway/kr22-web-event-kinesis",
            retention: logs.RetentionDays.TWO_WEEKS,
          })
        ),
      },
      defaultCorsPreflightOptions: corsOptions,
    });

    const firehoseRequestBodyMapping = dedent`
    {
      "DeliveryStreamName": "kr22_web_event_firehose",
      "Record": {
          #set ($json_body = $input.json('$'))
          #set ($json_headers = '')
          #set ($json_identity = "{""sourceIp"":""$context.identity.sourceIp"",""userAgent"":""$context.identity.userAgent"",""requestId"":""$context.requestId""}")
          #foreach($param in $input.params().header.keySet())
              #set ($escaped_header = $util.escapeJavaScript($input.params().header.get($param)).replaceAll("\\\\'","'"))
              #set ($json_headers = "$json_headers""$param"": ""$escaped_header"" ")
                  #if($foreach.hasNext)#set ($json_headers = "$json_headers,")#end
          #end
          #set ($out = "{""body"": \${json_body}, ""headers"": { \${json_headers} }, ""identity"": \${json_identity}, ""request_time"": \${context.requestTimeEpoch} }")
          "Data": "$util.base64Encode($out)"
      }
  }
    `.replace("\n", "");

    const firehoseIntegration = new apigateway.AwsIntegration({
      service: "firehose",
      action: "PutRecord",
      options: {
        credentialsRole: apigatewayRole,
        passthroughBehavior: apigateway.PassthroughBehavior.NEVER,
        requestTemplates: { "application/json": firehoseRequestBodyMapping },
        integrationResponses: [
          {
            statusCode: "200",
            selectionPattern: "200",
            responseTemplates: { "application/json": "{}" },
            responseParameters: integrationResponseParams,
          },
          {
            statusCode: "500",
            selectionPattern: "[5,4]d{2}",
            responseTemplates: {
              "application/json": '{"message": "$input.path("__type")"}',
            },
            responseParameters: integrationResponseParams,
          },
        ],
      },
    });

    const eventApi = restApi.root.addResource("events");
    eventApi.addMethod("POST", firehoseIntegration, {
      methodResponses: [
        {
          statusCode: "200",
          responseModels: { "application/json": apigateway.Model.EMPTY_MODEL },
          responseParameters: methodResponseParams,
        },
        {
          statusCode: "500",
          responseModels: { "application/json": apigateway.Model.ERROR_MODEL },
          responseParameters: methodResponseParams,
        },
      ],
    });
  }
}
