import urllib2

from io import BytesIO

from django.conf import settings

from PIL import Image
from neomodel import db
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.parsers import FileUploadParser, JSONParser


from plebs.neo_models import Pleb
from sb_registration.utils import delete_image

from .serializers import (UploadSerializer, ModifiedSerializer, CropSerializer,
                          URLContentSerializer, ThumbnailSerializer)
from .neo_models import (UploadedObject, URLContent)
from .utils import (resize_image, crop_image2, check_sagebrew_url,
                    thumbnail_image, upload_modified_image)


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
        croppic = request.query_params.get('croppic', 'false').lower()
        file_object = request.data.get('file_object', None)
        if file_object is None:
            file_object = request.data.get('file', None)
        if file_object is None:
            file_object = request.data.get('img', None)
        serializer = self.get_serializer(
            data={"file_object": file_object},
            context={'request': request})
        if serializer.is_valid():
            owner = Pleb.get(request.user.username)
            upload = serializer.save(owner=owner)
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

        img_file = urllib2.urlopen(request.data['imgUrl'])
        read_file = img_file.read()
        file_object = BytesIO(read_file)
        image = Image.open(file_object)
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
        cropped_image = crop_image2(image, crop_data['crop_width'],
                                    crop_data['crop_height'],
                                    crop_data['image_x1'],
                                    crop_data['image_y1'])
        # Fill cropped image into buffer
        file_stream = BytesIO()
        cropped_image.save(file_stream, format=image_format)
        file_stream.seek(0)
        # Upload cropped pic and then run serializer
        # Not the best solution but simplifies the logic. If someone has a
        # better approach feel free to update. Perhaps an InMemoryFile passed
        # to the serializer
        file_name = "%s-%sx%s.%s" % (object_uuid, crop_data['crop_width'],
                                     crop_data['crop_height'],
                                     image_format.lower())
        serializer = upload_modified_image(
            file_name, file_stream.read(), request, object_uuid)

        if serializer.is_valid():
            owner = Pleb.get(request.user.username)
            upload = serializer.save(owner=owner)
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

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated,],
                  serializer_class=ThumbnailSerializer,
                  parser_classes=(JSONParser,))
    def thumbnail(self, request, object_uuid=None):
        uploaded_object = self.get_object()
        img_file = urllib2.urlopen(uploaded_object.url)
        read_file = img_file.read()
        file_object = BytesIO(read_file)
        image = Image.open(file_object)
        image_format = image.format
        thumbnail_serializer = ThumbnailSerializer(data=request.data)
        if thumbnail_serializer.is_valid():
            thumbnail_data = thumbnail_serializer.data
        else:
            return Response(thumbnail_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        thumbnailed_image = thumbnail_image(
            image, thumbnail_data['thumbnail_height'],
            thumbnail_data['thumbnail_width'])
        # Fill thumbnailed image into buffer
        file_stream = BytesIO()
        thumbnailed_image.save(file_stream, format=image_format)
        file_stream.seek(0)
        # Upload cropped pic and then run serializer
        # Not the best solution but simplifies the logic. If someone has a
        # better approach feel free to update. Perhaps an InMemoryFile passed
        # to the serializer
        file_name = "%s-%sx%s.%s" % (object_uuid,
                                     thumbnail_data['thumbnail_width'],
                                     thumbnail_data['thumbnail_height'],
                                     image_format.lower())
        serializer = upload_modified_image(
            file_name, file_stream.read(), request, object_uuid)

        if serializer.is_valid():
            owner = Pleb.get(request.user.username)
            upload = serializer.save(owner=owner)
            profile_page_url = reverse(
                "profile_page", kwargs={
                    "pleb_username": request.user.username},
                request=request)
            return Response({"status": "success", "url": upload.url,
                             "profile": profile_page_url},
                            status=status.HTTP_200_OK)
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
                    'RETURN CASE friend.active WHEN True THEN ' \
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
