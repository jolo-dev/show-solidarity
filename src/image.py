import base64
import io
from os import path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import cv2


class SolidarityImage:
    """Image class to define attribute"""

    thumb_width: int
    background_img: Image
    blur_radius: int

    def __init__(
        self,
        thumb_width: int = 200,
        background_img: str = path.join(
            path.dirname(__file__), "ukrainian-flag-circle.png"
        ),
        blur_radius: int = 10,
    ):
        self.thumb_width = thumb_width
        self.background_img = Image.open(background_img)
        self.blur_radius = blur_radius

    def decode_img(self, base64_encoded: str):
        """
        Decodes a base64 encoded string of an
        image and creates an image for further processing
        :params base64_encoded string of a base64 encoded image
        :return buffered image
        """

        msg = base64.b64decode(base64_encoded)
        buf = io.BytesIO(msg)
        image = Image.open(buf)
        return image

    def detect_face(self, image_path: str):
        """
        Returns an array of faces
        """
        classifier = path.join(
            path.dirname(__file__),
            "haarcascade_frontalface_default.xml",
        )
        img = cv2.imread(image_path)
        cascade = cv2.CascadeClassifier(classifier)
        faces = cascade.detectMultiScale(
            img, 1.1, 10, cv2.CASCADE_SCALE_IMAGE, (200, 200)
        )
        print(faces)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.imwrite(
                "detected.jpg", img[y - 600 : (y + 2 * 900), x - 400 : (x + 2 * 1000)]
            )
        return faces

    def mask_circle_solid(self, image: Image):
        """
        Helper to circle an Image
        Thanks to https://www.geeksforgeeks.org/cropping-an-image-in-a-circular-way-using-python/
        """

        height, width = image.size
        lum_img = Image.new("L", [height, width], 0)
        draw = ImageDraw.Draw(lum_img)
        draw.pieslice([(0, 0), (height, width)], 0, 360, fill=255, outline="white")
        img_arr = np.array(image)
        lum_img_arr = np.array(lum_img)
        final_img_arr = np.dstack((img_arr, lum_img_arr))
        return Image.fromarray(final_img_arr)

    def add_background_frame(self, image: Image):
        img: Image = self.mask_circle_solid(image)
        height, width = self.background_img.size
        offset = self.blur_radius * 2

        img = img.resize((height - 100, width - 100), Image.ANTIALIAS)

        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(
            (offset, offset, img.size[0] - offset, img.size[1] - offset), fill=255
        )
        mask = mask.filter(ImageFilter.GaussianBlur(self.blur_radius))

        self.background_img.paste(img, (50, 50), mask)
        self.background_img.save("result.png", quality=100)
