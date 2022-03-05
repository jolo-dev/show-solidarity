import base64
from os import path
from PIL import Image, ImageDraw, ImageFilter

# from PIL import Image
import pytest
from src.image import SolidarityImage


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


def test_detect_face(test_image: SolidarityImage):
    locations = test_image.detect_face(image_path)
    assert len(locations) == 1  # Because there is just one face


def test_circle(test_image: SolidarityImage):
    im: Image = test_image.mask_circle_solid(Image.open("detected.jpg"))
    # print(im.size)
    blur_radius = 10

    flag_circle = Image.open("src/ukrainian-flag-circle.png")

    height, width = flag_circle.size
    im = im.resize((height - 100, width - 100), Image.ANTIALIAS)

    offset = blur_radius * 2
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, im.size[0] - offset, im.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    flag_circle.paste(im, (50, 50), mask)
    flag_circle.save("test.png", quality=100)
