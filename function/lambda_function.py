from __future__ import print_function
import json
from PIL import Image
import urllib
from function.src.image import SolidarityImage

image = SolidarityImage()


# --------------- Main handler ------------------
def handler(event, _context):
    """
    Uses Rekognition APIs to detect faces for objects uploaded to S3.
    """

    # Get the object from the event.
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"])

    try:
        # Call rekognition DetectFaces API to detect Text in S3 object.
        response: Image = image.detect_faces(bucket, key)
        img = image.add_background_frame(response)
        image.write_image_to_s3(img, bucket, "result.png")
        return response
    except Exception as e:
        print(
            "Error processing object {} from bucket {}. Event {}".format(
                key, bucket, json.dumps(event, indent=2)
            )
        )
        raise e
