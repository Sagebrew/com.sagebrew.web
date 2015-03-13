import os
from uuid import uuid1
from django.conf import settings

from boto import connect_s3
from boto.s3.key import Key
from PIL import Image
from sb_registration.utils import upload_image


def get_image_s3(uuid):
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                      settings.AWS_SECRET_ACCESS_KEY)
    k = Key(conn.get_bucket(bucket))

def crop_image(image, height, width, x, y, f_uuid=None):
    if f_uuid is None:
        f_uuid = str(uuid1())
    with Image.open(image) as image:
        src_width, src_height = image.size
        if src_width < width or src_height < height:
            image.thumbnail((height, width), Image.ANTIALIAS)
            image_name = "%s-%sx%s" % (f_uuid, width, height)
            resized = image.resize((height, width), Image.ANTIALIAS)
            resized.save(image_name+".png")
        else:
            region = image.crop((x, y, x+width, y+height))
            image_name = "%s-%sx%s" % (f_uuid, width, height)
            region.save(image_name+".png")
        with open(image_name+".png") as cropped_image:
            res = upload_image(settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                               image_name, cropped_image)
            if isinstance(res, Exception):
                return res
        os.remove(image_name+".png")
    return res

def thumbnail_image(image, width, height, f_uuid=None):
    if f_uuid is None:
        f_uuid = str(uuid1())
    size = (width, height)
    image = Image.open(image)
    image.thumbnail(size, Image.ANTIALIAS)
    background = Image.new('RGBA', size, (255, 255, 255, 0))
    background.paste(image,
                     ((size[0] - image.size[0]) / 2, (size[1] -
                                                      image.size[1]) / 2))
    background.save(f_uuid+".png")
