from copy import deepcopy
from logging import getLogger

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
        object_uuid = self.request.query_params.get('object_uuid', None)
        croppic = self.request.query_params.get('croppic', 'false').lower()
        file_object = request.data.get('file', None)
        if file_object is None:
            file_object = request.data.get('img', None)

        if object_uuid is None:
            return Response({'detail': "Please ensure to include a unique "
                                       "filename in as a query parameter in "
                                       "your url. The query parameter that "
                                       "should be used is `filename`."},
                            status=status.HTTP_400_BAD_REQUEST)
        another_file_object = deepcopy(file_object)
        # Limit to 2.5 mb or 2500000 bytes
        file_size = file_object.size
        image = Image.open(another_file_object)
        image_format = image.format
        width, height = image.size
        request.data['object_uuid'] = object_uuid
        serializer = UploadSerializer(data=request.data,
                                      context={'request': request,
                                               "file_format": image_format,
                                               "file_size": file_size})

        file_name = "%s.%s" % (object_uuid, image_format.lower())
        if serializer.is_valid():
            owner = cache.get(request.user.username)
            if owner is None:
                owner = Pleb.nodes.get(username=request.user.username)
                owner.set(request.user.username, owner)
            upload = serializer.save(owner=owner, width=width, height=height,
                                     file_size=file_size,
                                     file_format=image_format,
                                     file_object=file_object,
                                     file_name=file_name)
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
        return Response({}, status=status.HTTP_200_OK)
