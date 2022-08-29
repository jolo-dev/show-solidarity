import base64
import io
from os import path, environ
from PIL import Image
import numpy as np
import pytest
from function.src.image import SolidarityImage
from moto import mock_s3
import boto3

"""
The test should follow this order
1. Decode image from base64 to Image
2. Write that decoded image (step 1) to the S3 source Bucket
3. Read that image from S3 source Bucket
4. Detect Faces
5. Make Circle
6. Put to result Bucket
"""

image_path = path.join(path.dirname(__file__), "test-image.png")
S3_BUCKET = "mybucket"
IMAGE_NAME = "test-image.png"


@pytest.fixture
def test_base64_encode():
    """Helper to decode test-image.png"""
    with open(image_path, "rb") as image_file:
        data = base64.b64encode(image_file.read())
        return data


@pytest.fixture
def test_image():
    solidarity_image = SolidarityImage()
    return solidarity_image


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    environ["AWS_ACCESS_KEY_ID"] = "testing"
    environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    environ["AWS_SECURITY_TOKEN"] = "testing"
    environ["AWS_SESSION_TOKEN"] = "testing"
    environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def s3(aws_credentials):
    with mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


def test_base64_encode_image(test_image: SolidarityImage, test_base64_encode: str):
    """Step 1: Decode image from base64 to image"""

    decoded_image = test_image.decode_img(test_base64_encode)
    assert decoded_image == Image.open(image_path)


def test_write_image_to_s3(test_image: SolidarityImage, s3):
    """Step 2: Write image to S3"""

    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    s3.create_bucket(Bucket=S3_BUCKET)
    test_image.write_image_to_s3(
        np.array(Image.open(image_path)), S3_BUCKET, IMAGE_NAME, "us-east-1"
    )
    result = s3.list_buckets()
    assert len(result["Buckets"]) == 1

    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    assert len(response["Contents"]) == 1
    assert response["Contents"][0]["Key"] == IMAGE_NAME


def test_read_image_from_s3(test_image: SolidarityImage, s3):
    """Step 3: Read that image from an S3 Bucket"""

    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    s3.create_bucket(Bucket=S3_BUCKET)
    img_array = np.array(Image.open(image_path))
    file_stream = io.BytesIO()
    im = Image.fromarray(img_array)
    im.save(file_stream, format="JPEG")
    s3.put_object(Body=file_stream.getvalue(), Bucket=S3_BUCKET, Key=IMAGE_NAME)

    result = test_image.read_image_from_s3(S3_BUCKET, IMAGE_NAME, "us-east-1")

    assert result is not None
    # Need to check the attributes because PIL would check the random hex numbers
    assert result.size == Image.open(image_path).size
    assert result.format == Image.open(image_path).format
    assert result.im == Image.open(image_path).im
    assert result.height == Image.open(image_path).height
    assert result.width == Image.open(image_path).width
    assert result.mode == Image.open(image_path).mode


# @mock_rekognition
# def test_detect_face(test_image: SolidarityImage, s3):
#     """Step 4: Detect Faces
#     Unfortunately, the method "detect_faces" has not been implemented in moto (28/08/2022)
#     Will test in the integration test
#     """
#     # Need to create bucket and put the image inside that before rekognition can use it
#     s3.create_bucket(Bucket=S3_BUCKET)
#     img_array = np.array(Image.open(image_path))
#     file_stream = io.BytesIO()
#     im = Image.fromarray(img_array)
#     im.save(file_stream, format="PNG")
#     s3.put_object(Body=file_stream.getvalue(), Bucket=S3_BUCKET, Key=IMAGE_NAME)

#     locations = test_image.detect_faces(S3_BUCKET, IMAGE_NAME)
#     assert np.array(locations) == np.array(Image.open("/tmp/detected.jpg"))


def test_circle(test_image: SolidarityImage):
    """Step 5: Make Circle"""

    img_array = test_image.add_background_frame(Image.open(image_path))
    file_stream = io.BytesIO(img_array)
    im = Image.open(file_stream)
    im.save("/tmp/detected.jpg", format="png")
    # Should try detect one face on the result.png
    assert Image.open("tests/result.jpg") == Image.open("/tmp/detected.jpg")
