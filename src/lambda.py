from __future__ import print_function
import boto3
import json
import urllib

rekognition_client = boto3.client("rekognition")
s3_client = boto3.client("s3")

# --------------- Helper Functions to call Rekognition APIs ------------------


def detect_faces(bucket, key):
    response = rekognition_client.detect_faces(
        Image={"S3Object": {"Bucket": bucket, "Name": key}}
    )
    return response


# --------------- Main handler ------------------
def handler(event, _context):
    """
    Uses Rekognition APIs to detect faces for objects uploaded to S3.
    """
    # Log the the received event locally.
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event.
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"])

    try:
        # Call rekognition DetectText API to detect Text in S3 object.
        response = detect_faces(bucket, key)
        faces = [face["BoundingBox"] for face in response["FaceDetails"]]

        return faces
    except Exception as e:
        print(
            "Error processing object {} from bucket {}. Event {}".format(
                key, bucket, json.dumps(event, indent=2)
            )
        )
        raise e
