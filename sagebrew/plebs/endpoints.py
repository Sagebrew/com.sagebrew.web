from logging import getLogger

from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import logout

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination

from neomodel import db

from sagebrew import errors

from api.utils import request_to_api
from api.permissions import IsSelfOrReadOnly, IsSelf, IsOwnerOrAdmin
from sb_base.utils import get_filter_params
from sb_base.neo_models import SBContent
from sb_base.serializers import MarkdownContentSerializer
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_votes.serializers import VoteSerializer

from .serializers import (UserSerializer, PlebSerializerNeo, AddressSerializer,
                          FriendRequestSerializer)
from .neo_models import Pleb, Address, FriendRequest
from .utils import get_filter_by

logger = getLogger('loggly_logs')


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.nodes.all()
    serializer_class = AddressSerializer
    lookup_field = 'object_uuid'

    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def get_object(self):
        return Address.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        pleb = Pleb.nodes.get(username=self.request.user.username)
        instance = serializer.save()
        instance.owned_by.connect(pleb)
        instance.save()
        pleb.address.connect(instance)
        pleb.save()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)

    def retrieve(self, request, *args, **kwargs):
        single_object = self.get_object()
        serializer = self.get_serializer(single_object, context={
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

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        logout(self.request)
        # TODO we can also go and delete the pleb and content from here
        # or require additional requests but think we could spawn a task
        # that did all that deconstruction work rather than requiring an
        # app the hit a thousand endpoints.


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PlebSerializerNeo
    lookup_field = "username"
    queryset = Pleb.nodes.all()
    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_object(self):
        return Pleb.nodes.get(username=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        """
        Currently a profile is generated for a user when the base user is
        created. We currently don't support creating a profile through an
        endpoint due to the confirmation process and links that need to be
        made.
        :param request:
        :return:
        """
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def solutions(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def questions(self, request, username=None):
        filter_by = request.query_params.get('filter', "")
        try:
            additional_params = get_filter_params(filter_by, SBContent())
        except(IndexError, KeyError, ValueError):
            return Response(errors.QUERY_DETERMINATION_EXCEPTION,
                            status=status.HTTP_400_BAD_REQUEST)
        query = 'MATCH (a:Pleb {username: "%s"})-[:OWNS_QUESTION]->' \
                '(b:Question) WHERE b.to_be_deleted=false' \
                ' %s RETURN b' % (username, additional_params)
        res, col = db.cypher_query(query)
        queryset = [Question.inflate(row[0]) for row in res]

        page = self.paginate_queryset(queryset)
        serializer = QuestionSerializerNeo(page, many=True,
                                           context={'request': request})
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'])
    def public_content(self, request, username=None):
        filter_by = request.query_params.get('filter', "")
        try:
            additional_params = get_filter_params(filter_by, SBContent())
        except(IndexError, KeyError, ValueError):
            return Response(errors.QUERY_DETERMINATION_EXCEPTION,
                            status=status.HTTP_400_BAD_REQUEST)
        query = 'MATCH (b:`SBPublicContent`)-[:OWNED_BY]->(a:Pleb ' \
                '{username: "%s"}) ' \
                'WHERE b.to_be_deleted=false ' \
                ' %s RETURN b' % (username, additional_params)

        res, col = db.cypher_query(query)
        queryset = [SBContent.inflate(row[0]) for row in res]

        page = self.paginate_queryset(queryset)
        serializer = MarkdownContentSerializer(page, many=True,
                                               context={'request': request})
        return self.get_paginated_response(serializer.data)

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
        query = 'MATCH (a:Pleb {username: "%s"})-' \
                '[:FRIENDS_WITH {currently_friends: true}]->' \
                '(b:Pleb) RETURN b' % (username)
        res, col = db.cypher_query(query)
        queryset = [Pleb.inflate(row[0]) for row in res]
        html = self.request.query_params.get('html', 'false')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         context={'request': request})
        if html == 'true':
            html_array = []
            for item in serializer.data:
                html_array.append(
                    render_to_string('friend_block.html', dict(item)))
            return self.get_paginated_response(html_array)
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def friend_requests(self, request, username=None):
        # TODO we should probably make some sort of "notification" list view
        # or it can be more specific and be a friend request list view. But
        # that way we can get the pagination functionality easily and break out
        # html rendering. We can wait on it though until we transition to
        # JS framework
        single_object = self.get_object()
        if isinstance(single_object, Response):
            return single_object
        friend_requests = single_object.get_friend_requests_received()

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
                friend_url = "%s?expand=true" % reverse(
                    'profile-detail', kwargs={
                        'username': friend_request["from"]},
                    request=request)
                response = request_to_api(friend_url, request.user.username,
                                          req_method="GET")
                friend_request["from"] = response.json()
        if html == 'true':
            html = render_to_string('friend_request_wrapper.html',
                                    {"requests": friend_requests})
            return Response(html, status=status.HTTP_200_OK)
        return Response(friend_requests, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def notifications(self, request, username=None):
        single_object = self.get_object()
        if isinstance(single_object, Response):
            return single_object
        notifications = single_object.get_notifications()
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
                friend_url = reverse(
                    'profile-detail', kwargs={
                        'username': notification["from_info"]["username"]},
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
        single_object = self.get_object()
        reputation = {"reputation": single_object.reputation}
        return Response(reputation, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def local_representatives(self, request, username=None):
        pass

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def senators(self, request, username=None):
        single_object = self.get_object()
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
        single_object = self.get_object()
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

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def address(self, request, username=None):
        single_object = self.get_object()
        try:
            address = single_object.address.all()[0]
        except(IndexError):
            return Response(errors.CYPHER_INDEX_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        address_serializer = AddressSerializer(address,
                                               context={'request': request})
        return Response(address_serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def privileges(self, request, username=None):
        pass

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def actions(self, request, username=None):

        pass

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def restrictions(self, request, username=None):
        pass

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def is_beta_user(self, request, username=None):
        return Response({'is_beta_user': self.get_object().is_beta_user()},
                        status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def votes(self, request, username=None):
        filter_by = request.query_params.get('filter', "")
        try:
            additional_params = get_filter_params(filter_by, SBContent())
        except(IndexError, KeyError, ValueError):
            return Response(errors.QUERY_DETERMINATION_EXCEPTION,
                            status=status.HTTP_400_BAD_REQUEST)
        query = 'MATCH (b:`SBPublicContent`)-[:OWNED_BY]->(a:Pleb ' \
                '{username: "%s"}) ' \
                'WHERE b.to_be_deleted=false ' \
                ' %s RETURN b' % (username, additional_params)

        res, col = db.cypher_query(query)
        queryset = [SBContent.inflate(row[0]) for row in res]

        page = self.paginate_queryset(queryset)
        serializer = VoteSerializer(page, many=True,
                                    context={'request': request})
        return self.get_paginated_response(serializer.data)


class FriendRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FriendRequestSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        filter_by = self.request.query_params.get("filter", "")
        filtered = get_filter_by(filter_by)
        query = "MATCH (p:Pleb {username:'%s'})-%s-(r:FriendRequest) RETURN r" \
                % (self.request.user.username, filtered)
        res, col = db.cypher_query(query)
        queryset = [FriendRequest.inflate(row[0]) for row in res]
        return queryset

    def get_object(self):
        return FriendRequest.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)
