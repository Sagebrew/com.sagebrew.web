import bleach
import string
import urllib
import cStringIO
from PIL import Image

from api.utils import smart_truncate

from logging import getLogger
logger = getLogger("loggly_logs")

"""
def crop_image(image, height, width, x, y, f_uuid=None):
    if f_uuid is None:
        f_uuid = str(uuid1())
    with Image.open(image) as image:
        src_width, src_height = image.size
        if src_width < width or src_height < height:
            image.thumbnail((height, width), Image.ANTIALIAS)
            image_name = "%s-%sx%s" % (f_uuid, width, height)
            resized = image.resize((height, width), Image.ANTIALIAS)
            resized.save(image_name + ".png")
        else:
            region = image.crop((x, y, x + width, y + height))
            image_name = "%s-%sx%s" % (f_uuid, width, height)
            region.save(image_name + ".png")
        with open(image_name + ".png") as cropped_image:
            res = upload_image(settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                               image_name, cropped_image)
            if isinstance(res, Exception):
                return res
        os.remove(image_name + ".png")
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
    background.save(f_uuid + ".png")
"""


def resize_image(image, resize_width, resize_height):
    """
    This function will resize an image based upon the given width and height.
    If you use this to resize make sure you do any aspect ratio calculations
    before passing the values to this function as this does not attempt to
    maintain any aspect ratio.

    :param image:
    :param resize_width:
    :param resize_height:
    :return:
    """
    size = (int(float(resize_width)), int(float(resize_height)))
    resized = image.resize(size, Image.ANTIALIAS)
    return resized


def crop_image2(image, width, height, x, y):
    region = image.crop((x, y, x + width, y + height))
    return region


def parse_page_html(soupified, url, content_type='html/text'):
    logger.info(soupified)
    width = 0
    height = 0
    image = soupified.find(attrs={"property": "og:image"})
    title = soupified.find(attrs={"property": "og:title"})
    description = soupified.find(attrs={"property": "og:description"})
    try:
        image = filter(lambda x: x in string.printable,
                       bleach.clean(image.get('content')))
    except AttributeError:
        image = url
    try:
        title = filter(lambda x: x in string.printable,
                       bleach.clean(title.get('content')))
    except AttributeError:
        pass
    try:
        description = smart_truncate(
            filter(lambda x: x in string.printable,
                   bleach.clean(description.get('content'))))
    except AttributeError:
        pass
    if 'image' in content_type:
        temp_file = cStringIO.StringIO(urllib.urlopen(image).read())
        im = Image.open(temp_file)
        width, height = im.size
    return title, description, image, width, height
