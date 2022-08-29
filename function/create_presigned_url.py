import json


def handler(event, _context):
    """
    Creates a presigned URL and return that to the client
    """
    # Get the object from the event.
    bucket = event["bucketName"]
    key = event["key"]

    try:
        return {
            "key": key,
            "bucketName": bucket,
        }

    except Exception as e:
        print(
            "Error putting object {} to bucket {}. Event {}".format(
                key, bucket, json.dumps(event, indent=2)
            )
        )
        raise e
