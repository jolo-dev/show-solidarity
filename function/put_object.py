from src.image import SolidarityImage
import json
import numpy as np

image = SolidarityImage()


def handler(event, _context):
    """
    Uses Rekognition APIs to detect faces for objects uploaded to S3.
    """
    print(event)

    # Get the object from the event.
    bucket = event["bucket_name"]
    key = event["key"]
    image_base64 = event["body"]

    try:
        source_image = image.decode_img(image_base64)
        # Call rekognition DetectFaces API to detect Text in S3 object.
        image.write_image_to_s3(np.array(source_image), bucket, key)

    except Exception as e:
        print(
            "Error putting object {} to bucket {}. Event {}".format(
                key, bucket, json.dumps(event, indent=2)
            )
        )
        raise e
