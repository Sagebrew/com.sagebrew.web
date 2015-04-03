from logging import getLogger

from django.template.loader import render_to_string
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
from sb_docstore.utils import get_notification_docs
from api.permissions import IsSelfOrReadOnly, IsSelf
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
    def unfriend(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def friends(self, request, username=None):
        # Discuss, does it make more sense to have friends here or have a
        # separate endpoint /v1/friends/ that just
        # lists all the friends for the user who is making the query? I think
        # both places are valid. /v1/profiles/username/friends does enable you
        # to look at friends of friends more easily
        # However /v1/friends/username/ allows for a simpler defriend and
        # accessing method as you're able to go from
        # /v1/friends/ to /v1/friends/username/ to your method rather than
        # /v1/profiles/username/friends/ to /v1/profiles/username/ to your
        # method. But maybe we make both available.
        single_object = self.get_object(username=username)
        if isinstance(single_object, Response):
            return single_object
        try:
            friends = single_object.get_friends()
        except(CypherException, IOError) as e:
            logger.exception("ProfileGenericViewSet friends")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = self.serializer_class(
            friends, context={"request": request}, many=True)
        # TODO implement expand functionality
        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def friend_requests(self, request, username=None):
        single_object = self.get_object(username=username)
        if isinstance(single_object, Response):
            return single_object
        try:
            friend_requests = single_object.get_friend_requests_received()
        except(CypherException, IOError) as e:
            logger.exception("ProfileGenericViewSet friends")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        expand = self.request.QUERY_PARAMS.get('expand', "false").lower()
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            expand = 'true'

        for friend_request in friend_requests:
            if expand == "false":
                friend_request["from"] = reverse(
                    'profile-detail',
                    kwargs={'username': friend_request["from"]},
                    request=request)
            else:
                friend_url = reverse('profile-detail',
                    kwargs={'username': friend_request["from"]},
                    request=request)
                response = request_to_api(friend_url, request.user.username,
                                          req_method="GET")
                friend_request["from"] = response.json()
            if html == 'true':
                full_from_user = request_to_api(
                    friend_request['from']['base_user'], request.user.username,
                    req_method='GET')
                friend_request['full_from_user'] = full_from_user.json()
        if html == 'true':
            html = render_to_string('friend_request_wrapper.html',
                                    {"requests": friend_requests})
            return Response(html, status=status.HTTP_200_OK)
        return Response(friend_requests, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def notifications(self, request, username=None):
        single_object = self.get_object(username=username)
        if isinstance(single_object, Response):
            return single_object
        try:
            notifications = single_object.get_notifications()
        except(CypherException, IOError) as e:
            logger.exception("ProfileGenericViewSet friends")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        expand = self.request.QUERY_PARAMS.get('expand', "false").lower()
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            expand = 'true'
        for notification in notifications:
            if expand == "false":
                notification["from"] = reverse(
                    'profile-detail',
                    kwargs={'username': notification["from_info"]["username"]},
                    request=request)
            else:
                friend_url = reverse('profile-detail',
                    kwargs={'username': notification["from_info"]["username"]},
                    request=request)
                response = request_to_api(friend_url, request.user.username,
                                          req_method="GET")
                notification["from"] = response.json()
            if html == 'true':
                from_user_response = request_to_api(
                    notification['from']['base_user'], request.user.username,
                    req_method='GET')
                notification['from'] = from_user_response.json()
        if html == 'true':
            html = render_to_string('notifications.html',
                                {"notifications": notifications})
            return Response(html, status=status.HTTP_200_OK)
        return Response(notifications, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def reputation(self, request, username=None):
        single_object = self.get_object(username=username)
        if isinstance(single_object, Response):
            return single_object
        reputation = {"reputation": single_object.reputation}
        return Response(reputation, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def local_representatives(self, request, username=None):
        pass

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def senators(self, request, username=None):
        single_object = self.get_object(username=username)
        if isinstance(single_object, Response):
            return single_object
        senators = single_object.get_senators()
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            sen_html = []
            for sen in senators:
                sen_html.append(
                    render_to_string('sb_home_section/sb_senator_block.html',
                                     sen))
            return Response(sen_html, status=status.HTTP_200_OK)
        return Response(senators, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def house_rep(self, request, username=None):
        single_object = self.get_object(username=username)
        if isinstance(single_object, Response):
            return single_object
        house_rep = single_object.get_house_rep()
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            house_rep_html = render_to_string(
                'sb_home_section/sb_house_rep_block.html', house_rep)
            return Response(house_rep_html, status=status.HTTP_200_OK)
        return Response(house_rep, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def campaigning_senators(self, request, username=None):
        pass

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def campaigning_representatives(self, request, username=None):
        pass

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def campaigning_presidents(self, request, username=None):
        pass

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def campaigning_local_representatives(self, request, username=None):
        pass