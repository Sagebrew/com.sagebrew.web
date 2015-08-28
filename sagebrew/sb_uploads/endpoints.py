import urllib2
import StringIO

from io import BytesIO
from uuid import uuid1
from copy import deepcopy
from logging import getLogger

from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.uploadhandler import TemporaryUploadedFile

from PIL import Image
from neomodel import db
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.parsers import FileUploadParser


from plebs.neo_models import Pleb
from sb_registration.utils import delete_image

from .serializers import (UploadSerializer, ModifiedSerializer, CropSerializer,
                          URLContentSerializer)
from .neo_models import (UploadedObject, URLContent)
from .utils import resize_image, crop_image2

logger = getLogger('loggly_logs')


class UploadViewSet(viewsets.ModelViewSet):
    """
    This endpoint enables users to upload files to the server for usage on
    the site.

    Limitations:
    The endpoint currently only supports images up to 20mb. The 20mb limitation
    is a self imposed limitation so that we aren't clogging up our S3 instance
    or our memory when multiple users are uploading images at the same time.
    We see this as a reasonable limitation as the majority of users that have
    uploaded images so far have selected images under 5mb in size.
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
            owner = Pleb.get(request.user.username)
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
            owner = Pleb.get(request.user.username)
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


class URLContentViewSet(viewsets.ModelViewSet):
    """
    This endpoint enables users to input URLs into content and create a URL
    """
    serializer_class = URLContentSerializer
    lookup_field = 'object_uuid'
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return URLContent.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    def get_queryset(self):
        username = self.request.query_params.get('user', None)
        if self.request.user.username == username or username is None:
            # Returns the urlcontent created by the user accessing the endpoint
            query = 'MATCH (a:Pleb {username:"%s"})<-[:OWNED_BY]-' \
                    '(b:URLContent) RETURN b ORDER BY b.created DESC' % \
                    self.request.user.username
        else:
            # Returns the urlcontent created by the user passed as a query
            # param but only if the current user is friends with that user
            query = 'MATCH (current:Pleb {username:"%s"})-' \
                    '[friend:FRIENDS_WITH]->(other:' \
                    'Pleb {username:"%s"})<-[:OWNED_BY]-(url:URLContent) ' \
                    'RETURN CASE friend.currently_friends WHEN True THEN ' \
                    'url END AS result ORDER BY result.created DESC' % \
                    (self.request.user.username, username)
        res, _ = db.cypher_query(query)
        return res

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        page = [URLContent.inflate(row[0]) for row in page]
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=Pleb.get(self.request.user.username))
            serializer = serializer.data
            if request.query_params.get('html', 'false').lower() == 'true':
                return Response({"html": render_to_string(
                    'expanded_url_content.html', serializer),
                    "serialized": serializer}, status=status.HTTP_200_OK)
            return Response(serializer, status=status.HTTP_200_OK)
