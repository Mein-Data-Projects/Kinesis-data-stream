import json
import boto3
import csv


def lambda_handler(event, context):
    if event:
        # Capture event details
        eventObj = event["Records"][0]
        sourceBucket = eventObj["s3"]["bucket"]["name"]
        csvkey = eventObj["s3"]["object"]["key"]

        # Set variable for resource
        s3 = boto3.resource("s3")

        # Read CSV content
        csv_object = s3.Object(sourceBucket, csvkey)
        csv_content = csv_object.get()["Body"].read().splitlines()

        # Placeholder list for JSON
        l = []

        for line in csv_content:
            x = json.dumps(line.decode("utf-8")).split(",")

            # Parse columns
            Id = str(x[0])
            Team = str(x[1])
            City = str(x[2])

            # Format JSON
            y = {"Id": Id, "Team": Team, "City": City}

            # Add to list
            l.append(y)

        # Ckean formatting
        jsonformatted = json.dumps(l)

        # Push to Kinesis stream
        kinesis = boto3.client("kinesis", region_name="us-east-2")
        stream_name = "my-demo-stream"

        payload = {"Data": jsonformatted}

        kinesis.put_record(
            StreamName=stream_name, Data=json.dumps(payload), PartitionKey="partition"
        )

        print("Success")
    return


# S3 (source bucket) -> lambda -> kinesis (Data Stream) -> Kinesis(firehose) -> s3 (Data lake)
