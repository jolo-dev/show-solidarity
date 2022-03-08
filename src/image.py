import base64
import io
from os import path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import boto3
import face_recognition

rekognition_client = boto3.client("rekognition")
s3_client = boto3.client("s3")


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

    def read_image_from_s3(self, bucket: str, key: str, region_name="eu-central-1"):
        """Load image file from s3.

        Parameters
        ----------
        bucket: string
            Bucket name
        key : string
            Path in s3

        Returns
        -------
        np array
            Image array
        """
        s3 = boto3.resource("s3", region_name)
        bucket = s3.Bucket(bucket)
        object = bucket.Object(key)
        response = object.get()
        file_stream = response["Body"]
        im = Image.open(file_stream)
        return im

    def detect_face_by_path(self, image_path: str):
        """
        Returns an array of faces
        """

        image = face_recognition.load_image_file(image_path)
        foo = Image.fromarray(image)
        width, height = foo.size
        print(width, height)
        # Find all the faces in the image using a pre-trained convolutional neural network.
        # This method is more accurate than the default HOG model, but it's slower
        # unless you have an nvidia GPU and dlib compiled with CUDA extensions. But if you do,
        # this will use GPU acceleration and perform well.
        # See also: find_faces_in_picture.py
        face_locations = face_recognition.face_locations(
            image, number_of_times_to_upsample=0, model="cnn"
        )

        for face_location in face_locations:

            # Print the location of each face in this image
            top_, right_, bottom_, left_ = face_location
            top = round(height * 0.338)
            left = round(width * 0.462)
            bottom = top + round(height * 0.261)
            right = left + round(width * 0.259)
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

    def detect_faces(self, bucket: str, key: str):
        """
        Returns an array of faces
        """

        face_locations = rekognition_client.detect_faces(
            Image={"S3Object": {"Bucket": bucket, "Name": key}}
        )

        image = self.read_image_from_s3(bucket, key)

        orig_width, orig_height = image.size

        for face in face_locations.FaceDetails:

            # Print the location of each face in this image
            width = face.BoundingBox.Width
            height = face.BoundingBox.Height
            left = face.BoundingBox.Left
            top = face.BoundingBox.Top

            top = round(orig_height * top)
            left = round(orig_width * left)
            bottom = top + round(orig_height * height)
            right = left + round(orig_width * width)

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
