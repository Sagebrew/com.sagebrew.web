import bleach
import string
import io
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
import requests
try:
    import HTMLParser
except ImportError:
    from html.parser import HTMLParser
from uuid import uuid1
from copy import deepcopy
from PIL import Image
from mimetypes import guess_extension

from django.core.files.uploadhandler import TemporaryUploadedFile
from django.conf import settings

from rest_framework import status

from api.utils import smart_truncate
from sb_registration.utils import upload_image

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
    cropped_image = image.crop((x, y, x + width, y + height))
    return cropped_image


def check_sagebrew_url(url, folder, file_name, file_object, type_known=True):
    # Check if a sagebrew url, https, and is stored in correct folder
    if url is None:
        return upload_image(folder, file_name, file_object, type_known)
    parsed_url = urlparse(url)
    if parsed_url.netloc not in settings.ALLOWED_HOSTS or \
            folder not in parsed_url.path or parsed_url.scheme == "https":
        url = upload_image(folder, file_name, file_object, type_known)
    return url


def is_absolute(url):
    return bool(urlparse(url).netloc)


def get_page_image(url, soup, content_type='html/text'):
    height = 0
    width = 0
    image = soup.find(attrs={"property": "og:image"})
    if 'image' not in content_type:
        try:
            image = filter(lambda x: x in string.printable,
                           bleach.clean(image.get('content')))
        except AttributeError:
            images = soup.find_all('img')
            for test_url in images:
                if is_absolute(test_url['src']):
                    image = test_url['src']
                    break
            try:
                if image[:2] == "//":
                    image = image[2:]
                    if "http" not in image:
                        image = "http://" + image
            except (TypeError, AttributeError):
                return image, height, width
    else:
        image = url
    if 'image' in content_type or image:
        res = requests.get(image)
        if res.status_code == status.HTTP_200_OK:
            try:
                temp_file = io.BytesIO(res.content)
            except IOError:  # pragma: no cover
                # this IOError catches issues created by passing StringIO some
                # corrupt or invalid data which we cannot test reliably
                # currently
                return "", height, width
            try:
                im = Image.open(temp_file)
                width, height = im.size
            except IOError:
                # this IOError handles the possibility of an SVG getting
                # passed here, PIL cannot open SVGs so the IOError handles that
                pass
            file_ext = guess_extension(res.headers['content-type'])
            image = upload_image(settings.AWS_UPLOAD_IMAGE_FOLDER_NAME,
                                 '%s%s' % (str(uuid1()), file_ext),
                                 temp_file, True)
        else:
            return "", height, width
    return image, height, width


def get_page_title(soup):
    html_parser = HTMLParser.HTMLParser()
    title = soup.find(attrs={"property": "og:title"})
    try:
        title = filter(lambda x: x in string.printable,
                       html_parser.unescape(
                           bleach.clean(title.get('content'))))
    except AttributeError:
        try:
            title = filter(
                lambda x: x in string.printable,
                html_parser.unescape(bleach.clean(
                    soup.find('title').string)))
        except AttributeError:
            pass
    return title


def get_page_description(soup):
    html_parser = HTMLParser.HTMLParser()
    description = soup.find(attrs={"property": "og:description"})
    try:
        description = smart_truncate(
            filter(lambda x: x in string.printable,
                   html_parser.unescape(bleach.clean(
                       description.get('content')))))
    except AttributeError:
        description = ""
    if description == "":
        try:
            description = smart_truncate(
                filter(lambda x: x in string.printable,
                       html_parser.unescape(bleach.clean(
                           soup.find(
                               attrs={"name": "description"}).get(
                               'content')))))
        except AttributeError:
            pass
    return description


def parse_page_html(soupified, url, content_type='html/text'):
    image, height, width = get_page_image(url, soupified, content_type)
    description = get_page_description(soupified)
    title = get_page_title(soupified)
    return title, description, image, width, height


def get_image_data(object_uuid, file_object):
    if isinstance(file_object, io.BytesIO):
        image = Image.open(file_object)
    else:
        another_file_object = deepcopy(file_object)
        if isinstance(another_file_object, TemporaryUploadedFile):
            image = Image.open(another_file_object.temporary_file_path())
        else:
            image = Image.open(another_file_object)
    image_format = image.format
    width, height = image.size
    file_name = "%s.%s" % (object_uuid, image_format.lower())

    return width, height, file_name, image


def thumbnail_image(image, resize_height, resize_width):
    """
    This function will take whatever image is passed and rescale the image to
    whatever height and width is passed but it will maintain aspect ratio.

    :param image_file:
    :param resize_height:
    :param resize_width:
    :return:
    """
    image.thumbnail((resize_width, resize_height), Image.ANTIALIAS)
    return image


def hamming_distance(s1, s2):
    """Return the Hamming distance between equal-length sequences"""
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(bool(ord(ch1) - ord(ch2)) for ch1, ch2 in zip(s1, s2))
