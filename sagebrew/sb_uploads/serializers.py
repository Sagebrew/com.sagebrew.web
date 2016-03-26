import requests
from bs4 import BeautifulSoup
import imagehash
from django.conf import settings

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from neomodel import DoesNotExist, UniqueProperty, db

from api.serializers import SBSerializer
from sb_registration.utils import upload_image

from .utils import parse_page_html
from .neo_models import UploadedObject, ModifiedObject, URLContent


class MediaType:

    def __init__(self):
        pass

    def __call__(self, value):
        allowed_ext = ['gif', 'jpeg', 'jpg', 'png', 'GIF', 'JPEG', 'JPG',
                       'PNG']
        if value not in allowed_ext:
            message = 'You have provided an invalid file type. ' \
                      'The valid file types are gif, jpeg, jpg, and png'
            raise serializers.ValidationError(message)
        return value


class FileSize:

    def __init__(self):
        pass

    def __call__(self, value):
        if value > 20000000:
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
    is_portrait = serializers.SerializerMethodField()

    def create(self, validated_data):
        owner = None
        folder = settings.AWS_PROFILE_PICTURE_FOLDER_NAME
        if 'owner' in validated_data:
            owner = validated_data.pop('owner')
        width = validated_data.pop('width')
        height = validated_data.pop('height')
        file_name = validated_data.pop('file_name')
        object_uuid = validated_data.pop('object_uuid')
        file_size = validated_data.pop('file_size')
        file_format = validated_data.pop('file_format')
        file_object = validated_data.pop('file_object')
        if 'folder' in validated_data:
            folder = validated_data.pop('folder')
        image = validated_data.pop('image')
        url = upload_image(folder, file_name, file_object, True)
        if image is not None:
            image_hash = imagehash.dhash(image)
        else:
            image_hash = None
        verify_unique = validated_data.pop('verify_unique', False)
        if verify_unique:
            query = 'MATCH (upload:UploadedObject) ' \
                    'WHERE upload.image_hash="%s" ' \
                    'RETURN true' % image_hash
            res, _ = db.cypher_query(query)
            if res.one:
                raise ValidationError("Image must be unique")

        if owner is not None:
            validated_data['owner_username'] = owner.username
        uploaded_object = UploadedObject(
            file_format=file_format, url=url, height=height,
            width=width, file_size=file_size, object_uuid=object_uuid,
            image_hash=image_hash).save()
        if owner is not None:
            uploaded_object.owned_by.connect(owner)
            owner.uploads.connect(uploaded_object)
        return uploaded_object

    def update(self, instance, validated_data):
        return None

    def get_is_portrait(self, instance):
        return instance.height > instance.width


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
    image_viewable = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    is_portrait = serializers.SerializerMethodField()

    def create(self, validated_data):
        owner = validated_data.pop('owner')
        if hasattr(owner, 'username'):
            validated_data['owner_username'] = owner.username
        new_url = validated_data['url']
        if 'http' not in validated_data['url']:
            new_url = "http://" + validated_data['url']
        try:
            return URLContent.nodes.get(url=validated_data['url'])
        except (URLContent.DoesNotExist, DoesNotExist):
            try:
                return URLContent.nodes.get(url=new_url)
            except (URLContent.DoesNotExist, DoesNotExist):
                pass
        if any(validated_data['url'] in s for s in settings.EXPLICIT_STIES):
            validated_data['is_explicit'] = True
        try:
            response = requests.get(new_url,
                                    headers={'content-type': 'html/text'},
                                    timeout=5)
        except requests.Timeout:
            return URLContent(url=new_url).save()
        except requests.ConnectionError:
            try:
                response = requests.get("http://www." + validated_data['url'],
                                        headers={"content-type": "html/text"},
                                        timeout=5)
            except requests.ConnectionError:
                return URLContent(url=new_url).save()
        if response.status_code != status.HTTP_200_OK:
            return URLContent(url=new_url).save()
        soupified = BeautifulSoup(response.text, 'html.parser')
        title, description, image, width, height = \
            parse_page_html(
                soupified, validated_data['url'],
                response.headers.get('Content-Type', 'html/text'))
        try:
            url_content = URLContent(selected_image=image, title=title,
                                     description=description,
                                     image_width=width, image_height=height,
                                     **validated_data).save()
        except UniqueProperty:
            return URLContent.nodes.get(url=validated_data['url'])

        # TODO determine if this is necessary
        # spawn_task(task_func=create_url_content_summary_task, task_param={
        #    'object_uuid': url_content.object_uuid
        # })
        url_content.owned_by.connect(owner)
        owner.url_content.connect(url_content)
        return url_content

    def get_images(self, instance):
        return instance.get_images()

    def get_image_viewable(self, instance):
        return instance.selected_image and not instance.is_explicit

    def get_is_portrait(self, instance):
        return instance.image_height > instance.image_width
