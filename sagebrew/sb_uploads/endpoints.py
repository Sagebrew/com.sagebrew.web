import urllib2
import StringIO

from io import BytesIO
from uuid import uuid1
from copy import deepcopy
from logging import getLogger

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadhandler import TemporaryUploadedFile

from PIL import Image
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.parsers import FileUploadParser

from plebs.neo_models import Pleb
from sb_registration.utils import delete_image

from .serializers import UploadSerializer, ModifiedSerializer, CropSerializer
from .neo_models import UploadedObject
from .utils import resize_image, crop_image2

logger = getLogger('loggly_logs')


class UploadViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = UploadSerializer
    lookup_field = 'object_uuid'
    parser_classes = (FileUploadParser, )
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return UploadedObject.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    def list(self, request, *args, **kwargs):
        response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                    "detail": "We do not allow users to query all the uploaded "
                              "files on the site.",
                    "developer_message":
                        "We're working on enabling easier access to files based"
                        " on user's defined permissions. "
                        "However this endpoint currently does not return any "
                        "file data."
                    }
        return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, *args, **kwargs):
        single_object = self.get_object()
        file_name = single_object.url
        file_name = file_name.split(settings.AWS_STORAGE_BUCKET_NAME + "/")
        delete_image(file_name)
        single_object.delete()
        return Response({"detail": None}, status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        object_uuid = self.request.query_params.get('object_uuid',
                                                    str(uuid1()))
        croppic = self.request.query_params.get('croppic', 'false').lower()
        markdown = self.request.query_params.get('markdown', 'false').lower()
        file_object = request.data.get('file', None)
        if file_object is None:
            file_object = request.data.get('img', None)
        file_size = file_object.size
        request.data['file_format'] = file_object.content_type.split('/')[1]
        request.data['file_size'] = file_size
        serializer = UploadSerializer(data=request.data,
                                      context={'request': request})
        if serializer.is_valid():
            another_file_object = deepcopy(file_object)
            if isinstance(another_file_object, TemporaryUploadedFile):
                image = Image.open(another_file_object.temporary_file_path())
            else:
                image = Image.open(another_file_object)
            image_format = image.format
            width, height = image.size
            request.data['object_uuid'] = object_uuid
            file_name = "%s.%s" % (object_uuid, image_format.lower())
            owner = cache.get(request.user.username)
            if owner is None:
                owner = Pleb.nodes.get(username=request.user.username)
                owner.set(request.user.username, owner)
            upload = serializer.save(owner=owner, width=width, height=height,
                                     file_object=file_object,
                                     file_name=file_name,
                                     object_uuid=object_uuid)
            if croppic == 'true':
                return Response({"status": "success",
                                 "url": upload.url,
                                 "width": upload.width,
                                 "height": upload.height},
                                status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def crop(self, request, object_uuid=None):
        resize = self.request.query_params.get("resize", "false").lower()
        croppic = self.request.query_params.get('croppic', 'false').lower()
        img_file = StringIO.StringIO(
            urllib2.urlopen(request.data['imgUrl']).read())
        image = Image.open(img_file)
        image_format = image.format
        crop_serializer = CropSerializer(data=request.data)
        if crop_serializer.is_valid():
            crop_data = crop_serializer.data
        else:
            return Response(crop_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if resize == 'true':
            image = resize_image(image, int(crop_data['resize_width']),
                                 int(crop_data['resize_height']))
        cropped = crop_image2(image, crop_data['crop_width'],
                              crop_data['crop_height'],
                              crop_data['image_x1'],
                              crop_data['image_y1'])
        file_stream = BytesIO()
        cropped.save(file_stream, image_format)
        file_size = file_stream.tell()
        file_stream.seek(0)
        request.data['file_size'] = file_size
        request.data['file_format'] = image_format
        serializer = ModifiedSerializer(data=request.data,
                                        context={"request": request})
        file_name = "%s-%sx%s.%s" % (object_uuid, crop_data['crop_width'],
                                     crop_data['crop_height'],
                                     image_format.lower())
        if serializer.is_valid():
            owner = cache.get(request.user.username)
            if owner is None:
                owner = Pleb.nodes.get(username=request.user.username)
                owner.set(request.user.username, owner)
            upload = serializer.save(owner=owner,
                                     width=crop_data['crop_width'],
                                     height=crop_data['crop_height'],
                                     file_object=file_stream,
                                     file_name=file_name,
                                     object_uuid=object_uuid)
            if croppic == 'true':
                profile_page_url = reverse(
                    "profile_page", kwargs={
                        "pleb_username": request.user.username},
                    request=request)
                return Response({"status": "success", "url": upload.url,
                                 "profile": profile_page_url},
                                status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
