import json
from PIL import Image
from src.image import SolidarityImage
import base64
import numpy as np
import io


image = SolidarityImage()


# --------------- Main handler ------------------
def handler(event, _context):
    """
    Uses Rekognition APIs to detect faces for objects uploaded to S3.
    """

    print(event["Records"])
    # Get the object from the event.
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    result_bucket = "solidarityimagestack-resultsolidarityimagebucket1-1fydr16r11ag"
    try:
        # Call rekognition DetectFaces API to detect Text in S3 object.
        response: Image = image.detect_faces(bucket, key)
        img_array = image.add_background_frame(response)
        file_stream = io.BytesIO(img_array)
        img = Image.open(file_stream)
        img.save(f"/tmp/${key}.jpg", format="png")
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
