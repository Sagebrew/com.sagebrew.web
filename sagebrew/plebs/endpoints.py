from dateutil import parser
from elasticsearch import Elasticsearch, NotFoundError

from django.template.loader import render_to_string
from django.templatetags.static import static
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.cache import cache
from django.template import RequestContext
from django.conf import settings

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import (RetrieveUpdateDestroyAPIView, ListAPIView)

from neomodel import db

from sagebrew import errors

from api.permissions import IsSelfOrReadOnly, IsSelf
from sb_base.utils import get_filter_params
from sb_base.neo_models import SBContent
from sb_base.serializers import MarkdownContentSerializer
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_public_official.serializers import PublicOfficialSerializer
from sb_public_official.neo_models import PublicOfficial
from sb_campaigns.neo_models import PoliticalCampaign
from sb_campaigns.serializers import PoliticalCampaignSerializer

from .serializers import (UserSerializer, PlebSerializerNeo, AddressSerializer,
                          FriendRequestSerializer)
from .neo_models import Pleb, Address, FriendRequest
from .utils import get_filter_by

from logging import getLogger
logger = getLogger('loggly_logs')


class AddressViewSet(viewsets.ModelViewSet):
    """
    This ViewSet provides all of the addresses associated with the currently
    authenticated user. We don't want to enable users to view all addresses
    utilized on the site from an endpoint but this endpoint allows for users
    to see and modify their own as well as create new ones.

    Limitations:
    Currently we don't have a way to determine which address is the current
    address. We also don't have an interface to generate additional addresses
    so the address input during registration is the only address ever listed
    even though this should not be expected as in the future the list will
    grow as we all things like hometown, previous residences, and additional
    homes to be listed.

    Improvements:
    We may want to transition this to /v1/me/addresses/ and
    /v1/me/addresses/{id}/.
    """
    serializer_class = AddressSerializer
    lookup_field = 'object_uuid'

    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address) RETURN b' % self.request.user.username
        res, col = db.cypher_query(query)
        return [Address.inflate(row[0]) for row in res]

    def get_object(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address {object_uuid: "%s"}) RETURN b' % (
                    self.request.user.username, self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return Address.inflate(res[0][0])

    def perform_create(self, serializer):
        pleb = Pleb.get(self.request.user.username)
        instance = serializer.save()
        instance.owned_by.connect(pleb)
        pleb.address.connect(instance)
        pleb.refresh()
        cache.set(pleb.username, pleb)

        return instance


class UserViewSet(viewsets.ModelViewSet):
    """
    This ViewSet provides interactions with the base framework user. If you
    need to create/destroy/modify this is where it should be done.

    Limitations:
    Currently we still manage user creation through a different interface
    in the registration application. Eventually we'll look to utilize this
    endpoint from the registration application to create the user and create
    a more uniform user creation process that can be used throughout our
    different systems.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            es.delete(index="full-search-base", doc_type='profile',
                      id=instance.username)
        except NotFoundError:
            pass
        logout(self.request)
        # TODO we can also go and delete the pleb and content from here
        # or require additional requests but think we could spawn a task
        # that did all that deconstruction work rather than requiring an
        # app the hit a thousand endpoints.


class ProfileViewSet(viewsets.ModelViewSet):
    """
    This endpoint provides information for each of the registered users. It
    should not be used for creating users though as we lean on the Framework
    to accomplish user creation and authentication. This however is where all
    non-base attributes can be accessed. Users can access any other user's
    information as long as their authenticated but are limited to Read access
    if they are not the owner of the profile.

    Limitations:
    Currently we don't have fine grained permissions that enable us to restrict
    access to certain fields based on friendship status or user set permissions.
    We instead manage this in the frontend and only allow users browsing the
    web interface to see certain information. This is all done in the template
    though and any tech savvy person will still be able to check out the
    endpoint for the information. We'll want to eventually limit that here
    or in the serializer rather than higher up on the stack.
    """
    serializer_class = PlebSerializerNeo
    lookup_field = "username"
    queryset = Pleb.nodes.all()
    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_object(self):
        return Pleb.get(self.kwargs[self.lookup_field])

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
                context = RequestContext(request, item)
                item['page_user_username'] = username
                html_array.append(render_to_string('friend_block.html',
                                                   context))
            return self.get_paginated_response(html_array)
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, ))
    def reputation(self, request, username=None):
        return Response({"reputation": self.get_object().reputation},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, ))
    def senators(self, request, username=None):
        # TODO this may be able to be refined to [:REPRESENTED_BY]->(s:Senator)
        senators = cache.get("%s_senators" % username)
        if senators is None:
            query = "MATCH (a:Pleb {username: '%s'})-[:HAS_SENATOR]->" \
                    "(s:PublicOfficial) RETURN s" % username
            res, col = db.cypher_query(query)
            senators = [PublicOfficial.inflate(row[0]) for row in res]
            cache.set("%s_senators" % username, senators)
        if len(senators) == 0:
            return Response("<small>Sorry we could not find your "
                            "Senators. Please alert us to our error!"
                            "</small>", status=status.HTTP_200_OK)
        html = self.request.query_params.get('html', 'false').lower()
        if html == 'true':
            sen_html = []
            for sen in senators:
                sen_html.append(
                    render_to_string('sb_home_section/sb_senator_block.html',
                                     PublicOfficialSerializer(sen).data))
            return Response(sen_html, status=status.HTTP_200_OK)
        return Response(PublicOfficialSerializer(senators, many=True).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, ))
    def house_representative(self, request, username=None):
        # TODO this may be able to be refined to
        # [:REPRESENTED_BY]->(s:HouseRepresentative)
        house_rep = cache.get("%s_house_representative" % username)
        if house_rep is None:
            query = "MATCH (a:Pleb {username: '%s'})-" \
                    "[:HAS_HOUSE_REPRESENTATIVE]->" \
                    "(s:PublicOfficial) RETURN s" % username
            res, col = db.cypher_query(query)
            try:
                house_rep = PublicOfficial.inflate(res[0][0])
                cache.set("%s_house_representative" % username, house_rep)
            except IndexError:
                return Response("<small>Sorry we could not find your "
                                "House Representative. Please alert us to "
                                "our error!</small>",
                                status=status.HTTP_200_OK)
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            house_rep_html = render_to_string(
                'sb_home_section/sb_house_rep_block.html',
                PublicOfficialSerializer(house_rep).data)
            return Response(house_rep_html, status=status.HTTP_200_OK)
        return Response(PublicOfficialSerializer(house_rep).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def president(self, request, username=None):
        president = cache.get("%s_president" % (username))
        if president is None:
            query = 'MATCH (p:Pleb {username:"%s"})-[:HAS_PRESIDENT]->' \
                    '(o:PublicOfficial) RETURN o' % (username)
            res, _ = db.cypher_query(query)
            try:
                president = PublicOfficial.inflate(res[0][0])
                cache.set("%s_president" % (username), president)
            except IndexError:
                return Response("<small>Sorry we could not find your "
                                "President. Please alert us to our error"
                                "!</small>",
                                status=status.HTTP_200_OK)
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            return Response(
                render_to_string('sb_home_section/sb_house_rep_block.html',
                                 PublicOfficialSerializer(president).data),
                status=status.HTTP_200_OK)
        return Response(PublicOfficialSerializer(president).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsSelf))
    def is_beta_user(self, request, username=None):
        return Response({'is_beta_user': self.get_object().is_beta_user()},
                        status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def possible_house_representatives(self, request, username=None):
        possible_reps = cache.get('%s_possible_house_representatives' %
                                  (username))
        if possible_reps is None:
            query = 'MATCH (p:Pleb {username: "%s"})-[:LIVES_AT]->' \
                    '(a:Address)-[:ENCOMPASSED_BY]->(l:Location)-' \
                    '[:POSITIONS_AVAILABLE]->(o:Position)-[:CAMPAIGNS]' \
                    '->(c:Campaign) WHERE c.active=true RETURN c LIMIT 5' % \
                    (username)
            res, _ = db.cypher_query(query)
            possible_reps = [PoliticalCampaign.inflate(row[0]) for row in res]
            cache.set('%s_possible_house_representatives' % (username),
                      possible_reps)
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            if not possible_reps:
                return Response("<small>Currently No Registered Campaigning "
                                "Representatives In Your Area</small>",
                                status=status.HTTP_200_OK)
            possible_rep_html = [
                render_to_string('sb_home_section/sb_potential_rep.html',
                                 possible_rep) for possible_rep in
                PoliticalCampaignSerializer(possible_reps, many=True).data]
            return Response(possible_rep_html, status=status.HTTP_200_OK)
        return Response(PoliticalCampaignSerializer(possible_reps,
                                                    many=True).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def possible_senators(self, request, username=None):
        possible_senators = cache.get('%s_possible_senators' %
                                      (username))
        if possible_senators is None:
            query = 'MATCH (p:Pleb {username: "%s"})-[:LIVES_AT]->' \
                    '(a:Address)-[:ENCOMPASSED_BY]->(l:Location)-' \
                    '[:ENCOMPASSED_BY]->(l2:Location)-' \
                    '[:POSITIONS_AVAILABLE]->(o:Position)-[:CAMPAIGNS]' \
                    '->(c:Campaign) WHERE c.active=true RETURN c LIMIT 5' % \
                    (username)
            logger.info(query)
            res, _ = db.cypher_query(query)
            possible_senators = [PoliticalCampaign.inflate(row[0])
                                 for row in res]
            logger.info(possible_senators)
            cache.set('%s_possible_senators' % (username),
                      possible_senators)
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            if not possible_senators:
                return Response("<small>Currently No Registered Campaigning "
                                "Senators In Your Area</small>",
                                status=status.HTTP_200_OK)
            possible_senators_html = [
                render_to_string('sb_home_section/sb_potential_rep.html',
                                 possible_sen) for possible_sen in
                PoliticalCampaignSerializer(possible_senators, many=True).data]
            return Response(possible_senators_html, status=status.HTTP_200_OK)
        return Response(PoliticalCampaignSerializer(possible_senators,
                                                    many=True).data,
                        status=status.HTTP_200_OK)


class MeRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    """
    This endpoint provides the ability to get information regarding the
    currently authenticated user. This way AJAX, Ember, and other front end
    systems don't need to know what username they should bake into a
    /profile/ url to get information on the signed in user.
    """
    serializer_class = PlebSerializerNeo
    lookup_field = "username"
    permission_classes = (IsAuthenticated, IsSelf)

    def get_object(self):
        return Pleb.get(self.request.user.username)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = dict(serializer.data)
        if serializer_data['wallpaper_pic'] is None:
            serializer_data['wallpaper_pic'] = static(
                'images/wallpaper_western.jpg')
        if serializer_data['profile_pic'] is None:
            serializer_data['profile_pic'] = static(
                'images/sage_coffee_grey-01.png')
        return Response(serializer_data)


class FriendRequestViewSet(viewsets.ModelViewSet):
    """
    This ViewSet enables the user that is currently authenticated to view and
    manage their friend requests. Instead of making a method view on a specific
    profile we took this approach to gain easy pagination and so that the entire
    suite of managing an object could be utilized.

    This endpoint is used to see who a user has sent a friend request to rather
    than who they have received one from.
    """
    serializer_class = FriendRequestSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        friend_requests = cache.get("%s_friend_requests" %
                                    (self.request.user.username))
        if friend_requests is None:
            filter_by = self.request.query_params.get("filter", "")
            filtered = get_filter_by(filter_by)
            query = "MATCH (p:Pleb {username:'%s'})-%s-(" \
                    "r:FriendRequest) RETURN distinct r" \
                    % (self.request.user.username, filtered)
            res, col = db.cypher_query(query)
            friend_requests = [FriendRequest.inflate(row[0]) for row in res]
            cache.set("%s_friend_requests" % (self.request.user.username),
                      friend_requests)
        return friend_requests

    def get_object(self):
        return FriendRequest.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def perform_destroy(self, instance):
        instance.request_from.disconnect(Pleb.get(self.request.user.username))
        query = 'MATCH (f:FriendRequest {object_uuid:"%s"})-[r:REQUEST_TO]->' \
                '(p:Pleb {username:"%s"}) DELETE r' % \
                (instance.object_uuid, self.request.user.username)
        db.cypher_query(query)
        instance.delete()
        cache.delete("%s_friend_requests" % self.request.user.username)


class FriendManager(RetrieveUpdateDestroyAPIView):
    """
    The Friend Manager expects to be placed on the /me endpoint so that it
    can assume to grab the currently signed in user to manage friends for.
    """
    serializer_class = PlebSerializerNeo
    lookup_field = "friend_username"
    permission_classes = (IsAuthenticated, IsSelf)

    def get_object(self):
        return Pleb.get(self.kwargs[self.lookup_field])

    def update(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, *args, **kwargs):
        friend = self.get_object()
        profile = Pleb.get(request.user.username)
        # TODO: Change this to modifying the relationship manager rather than
        # just disconnecting

        profile.friends.disconnect(friend)
        friend.friends.disconnect(profile)

        return Response({'detail': 'success'},
                        status=status.HTTP_204_NO_CONTENT)


class FriendRequestList(ListAPIView):
    """
    This endpoint assumes it is placed on a specific user endpoint where
    it can really on the currently logged in user to gather notifications
    for. It is not capable of being set on an arbitrary user's profile
    endpoint like other method endpoints we have.
    """
    serializer_class = FriendRequestSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:RECEIVED_A_REQUEST]->' \
                '(n:FriendRequest) RETURN n ORDER ' \
                'BY n.created DESC LIMIT 5' % (self.request.user.username)
        res, col = db.cypher_query(query)
        return [FriendRequest.inflate(row[0]) for row in res]

    def list(self, request, *args, **kwargs):
        """
        Had to overwrite this function to add a check for a query param being
        passed that when set to true will set all the user's current
        notifications to seen
        """
        seen = request.query_params.get('seen', 'false').lower()
        if seen == "true":
            Pleb.clear_unseen_friend_requests(request.user.username)
            # Set queryset to [] as this query param means they've already
            # loaded the initial queryset and just want to mark them as
            # seen
            queryset = []
        else:
            queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes((IsAuthenticated, ))
def friend_request_renderer(request, object_uuid=None):
    """
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    """
    html_array = []
    id_array = []
    notifications = FriendRequestList.as_view()(request)
    for notification in notifications.data['results']:
        notification['time_sent'] = parser.parse(notification['time_sent'])
        context = RequestContext(request, notification)
        html_array.append(render_to_string('friend_request_block.html',
                                           context))
        id_array.append(notification["id"])

    notifications.data['results'] = {
        "html": html_array, "ids": id_array,
        "unseen": FriendRequest.unseen(request.user.username)
    }
    return Response(notifications.data, status=status.HTTP_200_OK)
