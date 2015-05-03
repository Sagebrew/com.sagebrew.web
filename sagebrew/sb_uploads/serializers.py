from django.conf import settings

from rest_framework import serializers

from api.serializers import SBSerializer
from sb_registration.utils import upload_image

from .neo_models import UploadedObject, ModifiedObject

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
        logger.info('here')
        logger.info(value)
        if (value > 2500000):
            message = "Your file cannot be larger than 2.5mb. Please select " \
                      "a smaller file."
            raise serializers.ValidationError(message)
        return value


class UploadSerializer(SBSerializer):
    file_format = serializers.CharField(validators=[MediaType(), ])
    file_size = serializers.IntegerField(validators=[FileSize(), ])
    url = serializers.SerializerMethodField()

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
        uploaded_object = UploadedObject(
            file_format=file_format, url=url, height=height,
            width=width, file_size=file_size, object_uuid=object_uuid).save()
        uploaded_object.owned_by.connect(owner)
        owner.uploads.connect(uploaded_object)
        return uploaded_object

    def update(self, instance, validated_data):
        return None


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
                                         file_size=file_size).save()
        modified_object.owned_by.connect(owner)
        owner.uploads.connect(modified_object)
        parent_object = UploadedObject.nodes.get(object_uuid=object_uuid)
        parent_object.modifications.connect(modified_object)
        modified_object.modification_to.connect(parent_object)
        return modified_object
