import base64
import io
from os import path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import boto3

rekognition_client = boto3.client("rekognition")
s3_client = boto3.client("s3")


class SolidarityImage:
    """
    Image class which crops and composite an image from S3
    with given background image

    Parameters
        ----------
        thumb_width: int
            The width of thumbnail
        background_img: str
            The image of background which will be composite
            This image is already cropped and won't be processed
            default: ukrainian-flag-circle.png
        blur_radius: int
            Blur radius of the two composite images to show smooth transition
    """

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

        Parameters
        ----------
        base64_encoded: string
            base64 encoded string of an image

        Returns
        -------
        Buffered Image
        """

        msg = base64.b64decode(base64_encoded)
        buf = io.BytesIO(msg)
        image = Image.open(buf)
        return image

    def read_image_from_s3(self, bucket: str, key: str, region_name="eu-central-1"):
        """
        Load image file from s3.
        Took it from here https://stackoverflow.com/a/56341457

        Parameters
        ----------
        bucket: string
            Bucket name
        key : string
            Path in s3

        Returns
        -------
        PIL Image
        """
        s3 = boto3.resource("s3", region_name)
        bucket = s3.Bucket(bucket)
        object = bucket.Object(key)
        response = object.get()
        file_stream = response["Body"]
        im = Image.open(file_stream)
        return im

    def write_image_to_s3(
        self, img_array: np.array, bucket: str, key: str, region_name="eu-central-1"
    ):
        """
        Write an image array into S3 bucket
        Took it from here https://stackoverflow.com/a/56341457

        Parameters
        ----------
        img_array: np.array
            An image array converted to numpy array
        bucket: string
            Bucket name
        key : string
            Path in s3

        Returns
        -------
        None
        """
        s3 = boto3.resource("s3", region_name)
        bucket = s3.Bucket(bucket)
        object = bucket.Object(key)
        file_stream = io.BytesIO()
        im = Image.fromarray(img_array)
        im.save(
            file_stream, format="png"
        )  # Store in PNG because it supports transparency
        object.put(Body=file_stream.getvalue())

    def detect_faces(self, bucket: str, key: str):
        """
        Detect the Bounding Box returned by Amazon Rekognition
        and crops out the face respectively

        Parameters
        ----------
        bucket: string
            Bucket name
        key : string
            Path in s3

        Returns
        -------
        An Image
        """

        face_locations = rekognition_client.detect_faces(
            Image={"S3Object": {"Bucket": bucket, "Name": key}}
        )

        image = self.read_image_from_s3(bucket, key)
        orig_width, orig_height = image.size

        for face in face_locations["FaceDetails"]:

            # The coordinates of Bounding Box of Amazon Rekognition
            # Found more: https://docs.aws.amazon.com/rekognition/latest/APIReference/API_BoundingBox.html
            width = face["BoundingBox"]["Width"]
            height = face["BoundingBox"]["Height"]
            left = face["BoundingBox"]["Left"]
            top = face["BoundingBox"]["Top"]

            top = round(orig_height * top)
            left = round(orig_width * left)
            bottom = top + round(orig_height * height)
            right = left + round(orig_width * width)

            # You can access the actual face itself like this:

            face_image = image.crop(
                (
                    left - round(left / 2),
                    top - round(top / 2),
                    right + round(right / 6),
                    bottom + round(bottom / 6),
                )
            )
            # pil_image = Image.fromarray(face_image)
            face_image.save("/tmp/detected.jpg")
        return face_image

    def mask_circle_solid(self, image: Image):
        """
        Helper to circle an Image of the detected faces
        Thanks to https://www.geeksforgeeks.org/cropping-an-image-in-a-circular-way-using-python/

        Parameters
        ----------
        image: Image
            PIL image

        Returns
        -------
        Image by an Array of numpy array
        """

        # Draw a circle around the detected faces
        height, width = image.size
        lum_img = Image.new("L", [height, width], 0)
        draw = ImageDraw.Draw(lum_img)
        draw.pieslice([(0, 0), (height, width)], 0, 360, fill=255, outline="white")
        img_arr = np.array(image)
        lum_img_arr = np.array(lum_img)
        final_img_arr = np.dstack((img_arr, lum_img_arr))
        return Image.fromarray(final_img_arr)

    def add_background_frame(self, image: Image):
        """
        Composite the circle image with a blurred circle
        and save the result in a /tmp/

        Parameters
        ----------
        image: Image
            PIL image

        Returns
        -------
        Numpy array of the saved image
        """
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
        buffer = io.BytesIO()
        self.background_img.save(buffer, format="PNG", quality=100)
        return buffer.getvalue()
