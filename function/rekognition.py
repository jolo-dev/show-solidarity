import json
from PIL import Image
from src.image import SolidarityImage
import base64
import numpy as np


image = SolidarityImage()


# --------------- Main handler ------------------
def handler(event, _context):
    """
    Uses Rekognition APIs to detect faces for objects uploaded to S3.
    """

    # Get the object from the event.
    bucket = event["source"]["Payload"]["bucketName"]
    key = event["source"]["Payload"]["key"]
    result_bucket = event["body"]["resultBucketName"]
    print(bucket, key, result_bucket)
    try:
        # Call rekognition DetectFaces API to detect Text in S3 object.
        response: Image = image.detect_faces(bucket, key)
        img = image.add_background_frame(response)
        print(response, np.array(base64.b64encode(img)))
        image.write_image_to_s3(np.array(img), result_bucket, key)
        return {
            "body": base64.b64encode(img),
            "bucketName": result_bucket,
            "key": key,
        }
    except Exception as e:
        print(
            "Error processing object {} from bucket {}. Event {}".format(
                key, bucket, json.dumps(event, indent=2)
            )
        )
        raise e
