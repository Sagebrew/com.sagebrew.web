from uuid import uuid1
import requests
import urllib2
import pytz
from bs4 import BeautifulSoup
import imagehash
from datetime import datetime, timedelta

from django.conf import settings

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from neomodel import DoesNotExist, UniqueProperty, db

from api.serializers import SBSerializer

from .utils import (parse_page_html, get_image_data, get_file_info,
                    check_sagebrew_url, hamming_distance)
from .neo_models import UploadedObject, ModifiedObject, URLContent


def verify_hamming_distance(value, distance=11, time_frame=None):
    skip = 0
    if time_frame is not None:
        then = (datetime.now(pytz.utc) -
                timedelta(days=time_frame)).strftime("%s")
    else:
        return True
    while True:
        query = 'MATCH (news:NewsArticle)-[:IMAGE_ON_PAGE]->' \
                '(image:UploadedObject) WHERE image.created > %s ' \
                'RETURN image.image_hash ' \
                'SKIP %s LIMIT 100' % (then, skip)
        skip += 99
        res, _ = db.cypher_query(query)
        if not res.one:
            break
        for row in res:
            result = hamming_distance(row[0], str(value))
            if result < distance:
                raise ValidationError("Too close to existing images")
    return True


class UploadSerializer(SBSerializer):
    file_object = serializers.FileField(required=False, write_only=True)
    file_format = serializers.CharField(read_only=True)
    file_size = serializers.IntegerField(read_only=True)
    width = serializers.IntegerField(read_only=True)
    height = serializers.IntegerField(read_only=True)
    url = serializers.CharField(
        required=False,
        help_text="If you do not include a URL to an image you must "
                  "include a file object in your POST")
    is_portrait = serializers.SerializerMethodField()

    def validate(self, data):
        # This is abnormally long since we're not verifying actual user input
        # we're analyzing the image or url provided and then having to do
        # the validation on the populated parameters
        # Please note this is run after all other field validators
        # http://stackoverflow.com/questions/27591574/
        # order-of-serializer-validation-in-django-rest-framework
        request = self.context.get('request')
        verify_unique = self.context.get('verify_unique', False)
        check_hamming = self.context.get('check_hamming', False)
        file_object = data.get('file_object')
        folder = self.context.get(
            'folder', settings.AWS_PROFILE_PICTURE_FOLDER_NAME)
        url = data.get('url')
        if request is not None:
            data['object_uuid'] = request.query_params.get(
                'object_uuid', str(uuid1()))
            serializers.UUIDField().run_validators(data['object_uuid'])
        elif data.get('object_uuid') is None:
            data['object_uuid'] = str(uuid1())
        if file_object and url:
            raise ValidationError("Cannot process both a URL and a "
                                  "File at the same time")
        try:
            file_size, file_format, file_object = get_file_info(
                file_object, url)
        except (ValueError, urllib2.HTTPError, urllib2.URLError):
            raise ValidationError("Invalid URL")
        data['width'], data['height'], file_name, image = get_image_data(
            data['object_uuid'], file_object)

        if data['width'] < 100:
            raise ValidationError("Must be at least 100 pixels wide")
        if data['height'] < 100:
            raise ValidationError("Must be at least 100 pixels tall")
        if file_size > settings.ALLOWED_IMAGE_SIZE:
            raise ValidationError(
                "Your file cannot be larger than 20mb. Please select "
                "a smaller file.")
        if file_format not in settings.ALLOWED_IMAGE_FORMATS:
            raise serializers.ValidationError(
                'You have provided an invalid file type. '
                'The valid file types are gif, jpeg, jpg, and png')

        data['url'] = check_sagebrew_url(url, folder, file_name, file_object)
        data['image_hash'] = str(imagehash.dhash(image))
        if verify_unique:
            query = 'MATCH (upload:UploadedObject) ' \
                    'WHERE upload.image_hash="%s" ' \
                    'RETURN true' % data['image_hash']
            res, _ = db.cypher_query(query)
            if res.one:
                raise ValidationError("Image must be unique")
        if check_hamming:
            verify_hamming_distance(data['image_hash'],
                                    check_hamming.get('distance', 11),
                                    check_hamming.get('time_frame'))
        return data

    def validate_url(self, value):
        if "sponsored" in value:
            raise ValidationError("Cannot be a sponsored link")
        for site in settings.EXPLICIT_SITES:
            if site in value:
                raise ValidationError("Cannot include pornographic content")
        return value

    def create(self, validated_data):
        owner = None
        if 'owner' in validated_data:
            owner = validated_data.pop('owner')
        if owner is not None:
            validated_data['owner_username'] = owner.username
        if 'file_object' in validated_data:
            validated_data.pop('file_object', None)
        uploaded_object = UploadedObject(**validated_data).save()
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
        modified_object = ModifiedObject(
            owner_username=owner.username, **validated_data).save()
        modified_object.owned_by.connect(owner)
        owner.uploads.connect(modified_object)
        parent_object = UploadedObject.nodes.get(
            object_uuid=validated_data['object_uuid'])
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
        if any(validated_data['url'] in s for s in settings.EXPLICIT_SITES):
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
