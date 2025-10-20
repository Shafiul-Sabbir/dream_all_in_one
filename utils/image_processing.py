import os
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import sys

ALL_IMAGE_FORMAT_LIST = ['rgb', 'RGB', 'gif', 'GIF', 'pbm', 'PBM', 'pgm', 'PGM', 'ppm', 'PPM', 'tiff', 'TIFF', 'rast', 'RAST', 'xbm', 'XBM', 'jpeg', 'JPEG', 'jpg', 'JPG', 'bmp', 'BMP', 'png', 'PNG', 'webp', 'WEBP' , 'exr', 'EXR']

def resize_image(img_list):
    for imge in img_list:
        max_width, max_height = 750, 1000
        path = imge.path
        try:
            image = Image.open(path)
            width, height = image.size
            if width > max_width or height > max_height:
                if width > height:
                    w_h = (1000, 750)
                elif height > width:
                    w_h = (750, 1000)
                img = image.resize(w_h)
                img.save(path)
        except Exception:
            pass

def pil_image_to_uploaded_file(pil_image, name="temp.jpg"):
    buffer = BytesIO()
    pil_image.save(buffer, format="JPEG")  # বা PNG
    buffer.seek(0)
    return InMemoryUploadedFile(
        buffer,                # file
        field_name=None,       # field_name
        name=name,             # file name
        content_type="image/jpeg",
        size=sys.getsizeof(buffer),
        charset=None
    )

def parse_image_from_item(image_path: str):
    """
    Given an absolute image path, 
    return the opened image object and the file name.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Image name extract করা
    image_name = os.path.basename(image_path)

    # Image open করা
    image = Image.open(image_path)

    image_obj = {
        "image_name" : image_name,
        "image" : image,
    }

    return image_obj