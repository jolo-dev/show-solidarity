import base64
from os import path
from PIL import Image

# from PIL import Image
import pytest
from function.src.image import SolidarityImage


image_path = path.join(path.dirname(__file__), "test-image.jpeg")


@pytest.fixture
def test_base64_encode():
    with open(image_path, "rb") as image_file:
        data = base64.b64encode(image_file.read())
        return data


@pytest.fixture
def test_image():
    solidarity_image = SolidarityImage()
    return solidarity_image


def test_base64_encode_image(test_image: SolidarityImage, test_base64_encode: str):
    decoded_image = test_image.decode_img(test_base64_encode)
    assert decoded_image == Image.open(image_path)


def test_read_image_from_s3(test_image: SolidarityImage):
    test_image = test_image.read_image_from_s3("show-solidarity", "test-image.jpeg")
    assert test_image is not None


def test_detect_face(test_image: SolidarityImage):
    locations = test_image.detect_faces("show-solidarity", "test-image.jpeg")
    assert len(locations) == 1  # Because there should be just one face


def test_circle(test_image: SolidarityImage):
    detected = "detected.jpg"
    test_image.add_background_frame(Image.open(detected))
    # Should try detect one face on the result.png
    # locations = test_image.detect_faces("result.png")
    # assert len(locations) == 1  # Because there should be just one face
