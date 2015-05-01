import os
import magic

from django.core.cache import cache

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.parsers import FileUploadParser

from plebs.neo_models import Pleb

from .serializers import UploadSerializer
from .neo_models import UploadedObject


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

    def get_queryset(self):
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
        file_path = self.request.query_params.get('file_name', None)
        if file_path is None:
            return Response({'detail': "Please ensure to include a unique "
                                       "filename in as a query parameter in "
                                       "your url. The query parameter that "
                                       "should be used is `filename`."})
        media_type = magic.from_file(file_path, mime=True)
        # Limit to 5 mb or 5000000 bytes
        file_size = os.path.getsize(file_path)
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request,
                                                  "media_type": media_type,
                                                  "file_size": file_size})
        if serializer.is_valid():
            owner = cache.get(self.kwargs[self.lookup_field])
            if owner is None:
                profile = Pleb.nodes.get(
                    username=self.kwargs[self.lookup_field])
                owner.set(self.kwargs[self.lookup_field], profile)
            serializer.save(owner=owner)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user,
                        file_type=,
                        file=self.request.data['file'])

    @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    def crop(self, request, object_uuid=None):
        return Response({}, status=status.HTTP_200_OK)