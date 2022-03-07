import base64
import io
from os import path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import face_recognition


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
        # classifier = path.join(
        #     path.dirname(__file__),
        #     "haarcascade_frontalface_default.xml",
        # )
        # img = cv2.imread(image_path)
        # cascade = cv2.CascadeClassifier(classifier)
        # faces = cascade.detectMultiScale(
        #     img, 1.1, 10, cv2.CASCADE_SCALE_IMAGE, (200, 200)
        # )
        # print(faces)

        # for (x, y, w, h) in faces:
        #     cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
        #     cv2.imwrite(
        #         "detected.jpg", img[y - 600 : (y + 2 * 900), x - 400 : (x + 2 * 1000)]
        #     )
        # return faces

        image = face_recognition.load_image_file(image_path)

        # Find all the faces in the image using a pre-trained convolutional neural network.
        # This method is more accurate than the default HOG model, but it's slower
        # unless you have an nvidia GPU and dlib compiled with CUDA extensions. But if you do,
        # this will use GPU acceleration and perform well.
        # See also: find_faces_in_picture.py
        face_locations = face_recognition.face_locations(
            image, number_of_times_to_upsample=0, model="cnn"
        )

        # print(
        #     "I found {} face(s) in this photograph. {}".format(
        #         len(face_locations), face_locations
        #     )
        # )

        for face_location in face_locations:

            # Print the location of each face in this image
            top, right, bottom, left = face_location
            print(
                "A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(
                    top, left, bottom, right
                )
            )

            # You can access the actual face itself like this:
            face_image = image[
                top - round(top / 4) : bottom + round(bottom / 4),
                left - round(left / 4) : right + round(right / 4),
            ]
            pil_image = Image.fromarray(face_image)
            pil_image.save("detected.jpg")
        return face_locations

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
