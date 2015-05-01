import os
import imghdr
import StringIO

from django.conf import settings
from django.core.cache import cache

from PIL import Image
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.parsers import FileUploadParser

from plebs.neo_models import Pleb

from .serializers import UploadSerializer
from .neo_models import UploadedObject


from logging import getLogger
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
            object_uuid=self.kwargs[self.lookup_url_kwarg])

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

    def create(self, request, *args, **kwargs):
        file_path = self.request.query_params.get('filename', None)
        croppic = self.request.query_params.get('croppic', 'false').lower()
        file_object = request.data.get('file', None)
        if file_object is None:
            file_object = request.data.get('img', None)


        if file_path is None:
            return Response({'detail': "Please ensure to include a unique "
                                       "filename in as a query parameter in "
                                       "your url. The query parameter that "
                                       "should be used is `filename`."},
                            status=status.HTTP_400_BAD_REQUEST)
        img_info = imghdr.what(file_object)
        # Limit to 2.5 mb or 2500000 bytes
        file_size = file_object.size
        serializer = UploadSerializer(data=request.data,
                                      context={'request': request,
                                               "media_type": img_info,
                                               "file_size": file_size})

        image = Image.open(file_object)
        width, height = image.size
        if serializer.is_valid():
            owner = cache.get(request.user.username)
            if owner is None:
                owner = Pleb.nodes.get(username=request.user.username)
                owner.set(request.user.username, owner)
            upload = serializer.save(owner=owner, width=width, height=height,
                                     file_size=file_size, media_type=img_info,
                                     file_object=file_object,
                                     file_name=file_path)
            if croppic == 'true':
                return Response({"status": "success",
                                 "url": upload.url,
                                 "width": upload.width,
                                 "height": upload.height},
                                status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    def crop(self, request, object_uuid=None):
        return Response({}, status=status.HTTP_200_OK)
