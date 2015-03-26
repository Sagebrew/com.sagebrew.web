from logging import getLogger

from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination

from neomodel import CypherException

from sagebrew import errors

from api.utils import request_to_api
from api.permissions import IsSelfOrReadOnly
from sb_comments.serializers import CommentSerializer

from .serializers import UserSerializer, PlebSerializerNeo
from .neo_models import Pleb

logger = getLogger('loggly_logs')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)

    def retrieve(self, request, *args, **kwargs):
        single_object = self.get_object()
        serializer = self.serializer_class(single_object, context={
            'request': request})
        expand = self.request.QUERY_PARAMS.get('expand', "false").lower()
        rest_response = dict(serializer.data)

        profile_endpoint = reverse(
            'profile-detail', kwargs={
                'username': kwargs[self.lookup_field]},
            request=request)
        if expand == "false":
            rest_response["profile"] = profile_endpoint
        else:
            response = request_to_api(profile_endpoint, request.user.username,
                                      req_method="GET")
            rest_response["profile"] = response.json()

        return Response(rest_response, status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.GenericViewSet):
    serializer_class = PlebSerializerNeo
    lookup_field = "username"
    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        try:
            queryset = Pleb.nodes.all()
        except(CypherException, IOError):
            logger.exception("ProfileGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return queryset

    def get_object(self, username=None):
        try:
            queryset = Pleb.nodes.get(username=username)
        except(CypherException, IOError):
            logger.exception("ProfileViewSet get_object")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        if isinstance(queryset, Response):
            return queryset
        serializer = self.serializer_class(
            queryset, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, username=None):
        single_object = self.get_object(username=username)
        if isinstance(single_object, Response):
            return single_object
        serializer = self.serializer_class(single_object,
                                           context={'request': request})
        expand = self.request.QUERY_PARAMS.get('expand', "false").lower()

        # The cast to dict is necessary as serializer.data is immutable
        # Won't be necessary when we transition this to dynamo
        rest_response = dict(serializer.data)
        rest_response["profile_url"] = reverse(
            'profile_page', kwargs={'pleb_username': username}, request=request)
        if expand != "false":
            user_url = reverse(
                'user-detail', kwargs={'username': username}, request=request)
            response = request_to_api(user_url, request.user.username,
                                      req_method="GET")
            rest_response["base_user"] = response.json()
        return Response(rest_response, status=status.HTTP_200_OK)

    def destroy(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def solutions(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def questions(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'], serializer_class=CommentSerializer)
    def comments(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def friend(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def defriend(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)