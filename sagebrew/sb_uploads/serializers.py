from django.conf import settings

from rest_framework import serializers

from api.serializers import SBSerializer
from sb_registration.utils import upload_image

from .neo_models import UploadedObject

from logging import getLogger
logger = getLogger('loggly_logs')

"""
class MediaType:
    def __init__(self):
        pass

    def __call__(self, value):
        if (self.media_type not in ['']):
            message = 'Cannot edit Title when there have ' \
                      'already been solutions provided'
            raise serializers.ValidationError(message)
        return value

    def set_context(self, serializer_field):
        try:
            self.media_type = serializer_field.parent.instance.media_type
        except AttributeError:
            self.media_type = None
"""


class UploadSerializer(SBSerializer):
    media_type = serializers.CharField(required=False)
    url = serializers.SerializerMethodField()
    vote_on = serializers.SerializerMethodField()

    def create(self, validated_data):
        owner = validated_data.pop('owner', None)
        width = validated_data.pop('width', None)
        height = validated_data.pop('height', None)
        file_name = validated_data.pop('file_name', None)
        file_size = validated_data.pop('file_size', None)
        media_type = validated_data.pop('media_type', None)
        file_object = validated_data.pop('file_object', None)
        local_file = "%s/%s" % (settings.PROJECT_DIR, "test_file.jpg")
        output_stream = open(local_file, "wb")
        output_stream.write(file_object.read())
        url = upload_image(settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                           file_name, local_file, True)
        logger.info(url)
        uploaded_object = UploadedObject(media_type=media_type,
                                         url=url,
                                         height=height,
                                         width=width,
                                         file_size=file_size).save()
        uploaded_object.owned_by.connect(owner)
        owner.uploads.connect(uploaded_object)
        return uploaded_object

    def update(self, instance, validated_data):
        return None
