import requests
from bs4 import BeautifulSoup

from django.conf import settings
from django.template.loader import render_to_string

from rest_framework import serializers, status

from neomodel import DoesNotExist, UniqueProperty

from api.serializers import SBSerializer
from sb_registration.utils import upload_image

from .utils import parse_page_html
from .neo_models import UploadedObject, ModifiedObject, URLContent

from logging import getLogger
logger = getLogger('loggly_logs')


class MediaType:
    def __init__(self):
        pass

    def __call__(self, value):
        allowed_ext = ['gif', 'jpeg', 'jpg', 'png', 'GIF', 'JPEG', 'JPG',
                       'PNG']
        if (value not in allowed_ext):
            message = 'You have provided an invalid file type. ' \
                      'The valid file types are: %s' % (', '.join(allowed_ext))

            raise serializers.ValidationError(message)
        return value


class FileSize:
    def __init__(self):
        pass

    def __call__(self, value):
        if (value > 20000000):
            message = "Your file cannot be larger than 20mb. Please select " \
                      "a smaller file."
            raise serializers.ValidationError(message)
        return value


class UploadSerializer(SBSerializer):
    file_format = serializers.CharField(validators=[MediaType(), ])
    file_size = serializers.IntegerField(validators=[FileSize(), ])
    width = serializers.IntegerField(read_only=True)
    height = serializers.IntegerField(read_only=True)
    url = serializers.CharField(read_only=True)

    html = serializers.SerializerMethodField()

    def create(self, validated_data):
        owner = validated_data.pop('owner')
        width = validated_data.pop('width')
        height = validated_data.pop('height')
        file_name = validated_data.pop('file_name')
        object_uuid = validated_data.pop('object_uuid')
        file_size = validated_data.pop('file_size')
        file_format = validated_data.pop('file_format')
        file_object = validated_data.pop('file_object')
        url = upload_image(settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                           file_name, file_object, True)
        validated_data['owner_username'] = owner.username
        uploaded_object = UploadedObject(
            file_format=file_format, url=url, height=height,
            width=width, file_size=file_size, object_uuid=object_uuid).save()
        uploaded_object.owned_by.connect(owner)
        owner.uploads.connect(uploaded_object)
        return uploaded_object

    def update(self, instance, validated_data):
        return None

    def get_html(self, instance):
        return render_to_string('contained_image.html',
                                {"uploaded_object": instance})


class ModifiedSerializer(UploadSerializer):

    def create(self, validated_data):
        owner = validated_data.pop('owner')
        width = validated_data.pop('width')
        height = validated_data.pop('height')
        file_name = validated_data.pop('file_name')
        file_size = validated_data.pop('file_size')
        file_format = validated_data.pop('file_format').lower()
        file_object = validated_data.pop('file_object')
        object_uuid = validated_data.pop('object_uuid')
        url = upload_image(settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                           file_name, file_object, True)
        modified_object = ModifiedObject(file_format=file_format, url=url,
                                         height=height, width=width,
                                         file_size=file_size,
                                         owner_username=owner.username).save()
        modified_object.owned_by.connect(owner)
        owner.uploads.connect(modified_object)
        parent_object = UploadedObject.nodes.get(object_uuid=object_uuid)
        parent_object.modifications.connect(modified_object)
        modified_object.modification_to.connect(parent_object)
        return modified_object


class CropSerializer(serializers.Serializer):
    crop_width = serializers.IntegerField()
    crop_height = serializers.IntegerField()
    image_x1 = serializers.IntegerField()
    image_y1 = serializers.IntegerField()
    resize_width = serializers.FloatField()
    resize_height = serializers.FloatField()


class URLContentSerializer(SBSerializer):
    refresh_timer = serializers.IntegerField(read_only=True)
    url = serializers.CharField(required=True)
    description = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    selected_image = serializers.CharField(read_only=True)
    image_width = serializers.IntegerField(read_only=True)
    image_height = serializers.IntegerField(read_only=True)
    is_explicit = serializers.BooleanField(read_only=True)

    images = serializers.SerializerMethodField()

    def create(self, validated_data):
        owner = validated_data.pop('owner')
        validated_data['owner_username'] = owner.username
        new_url = validated_data['url']
        if 'http' not in validated_data['url']:
            new_url = 'https://' + validated_data['url']
        logger.info(new_url)
        try:
            return URLContent.nodes.get(url=validated_data['url'])
        except (URLContent.DoesNotExist, DoesNotExist):
            pass
        if any(validated_data['url'] in s for s in settings.EXPLICIT_STIES):
            validated_data['is_explicit'] = True
        try:
            response = requests.get(new_url,
                                    headers={'content-type': 'html/text'})
        except requests.ConnectionError:
            return URLContent(url=new_url).save()
        if response.status_code == status.HTTP_404_NOT_FOUND:
            logger.info('here')
            try:
                response = requests.get("https://www." + validated_data['url'],
                                        headers={"content-type": "html/text"})
                logger.info(response)
            except Exception as e:
                logger.info(e)
            except requests.ConnectionError as e:
                logger.info(e)
                return URLContent(url=new_url).save()
        logger.info(response.status_code)
        if response.status_code != status.HTTP_200_OK:
            return URLContent(url=new_url).save()
        soupified = BeautifulSoup(response.text, 'html.parser')
        title, description, image, width, height = \
            parse_page_html(
                soupified, validated_data['url'],
                response.headers.get('Content-Type', 'html/text'))
        logger.info(title)
        logger.info(description)
        logger.info(image)
        try:
            url_content = URLContent(selected_image=image, title=title,
                                     description=description,
                                     image_width=width, image_height=height,
                                     **validated_data).save()
        except UniqueProperty:
            return URLContent.nodes.get(url=validated_data['url'])
        url_content.owned_by.connect(owner)
        owner.url_content.connect(url_content)
        return url_content

    def get_images(self, instance):
        return instance.get_images()
