import stripe
import pytz
from datetime import datetime, timedelta
from dateutil import parser
from operator import attrgetter
from elasticsearch import Elasticsearch, NotFoundError

from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.cache import cache
from django.template import RequestContext
from django.conf import settings

from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (RetrieveUpdateDestroyAPIView, mixins)

from neomodel import db

from sagebrew import errors

from api.permissions import (IsSelfOrReadOnly, IsSelf,
                             IsAnonCreateReadOnlyOrIsAuthenticated)
from sb_base.utils import get_filter_params
from sb_base.neo_models import SBContent
from sb_base.serializers import MarkdownContentSerializer
from sb_posts.neo_models import Post
from sb_posts.serializers import PostSerializerNeo
from sb_questions.neo_models import Question, Solution
from sb_questions.serializers import (QuestionSerializerNeo,
                                      SolutionSerializerNeo)
from sb_public_official.serializers import PublicOfficialSerializer
from sb_public_official.neo_models import PublicOfficial
from sb_donations.neo_models import Donation
from sb_donations.serializers import DonationSerializer
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_updates.neo_models import Update
from sb_updates.serializers import UpdateSerializer
from sb_news.neo_models import NewsArticle
from sb_news.serializers import NewsArticleSerializer
from .serializers import (UserSerializer, PlebSerializerNeo, AddressSerializer,
                          FriendRequestSerializer, PoliticalPartySerializer,
                          InterestsSerializer)
from .neo_models import Pleb, Address, FriendRequest
from .utils import get_filter_by


def get_public_content(api, username, request):
        then = (datetime.now(pytz.utc) - timedelta(days=120)).strftime("%s")
        query = \
            '// Retrieve all the current users questions\n' \
            'MATCH (a:Pleb {username: "%s"})<-[:OWNED_BY]-' \
            '(questions:Question) ' \
            'WHERE questions.to_be_deleted = False AND questions.created > %s' \
            ' AND questions.is_closed = False ' \
            'RETURN questions, NULL AS solutions, ' \
            'questions.created AS created, NULL AS s_question UNION ' \
            '// Retrieve all the current users solutions\n' \
            'MATCH (a:Pleb {username: "%s"})<-' \
            '[:OWNED_BY]-(solutions:Solution)<-' \
            '[:POSSIBLE_ANSWER]-(s_question:Question) ' \
            'WHERE s_question.to_be_deleted = False ' \
            'AND solutions.created > %s' \
            ' AND solutions.is_closed = False ' \
            'AND s_question.is_closed = False ' \
            'RETURN solutions, NULL AS questions, ' \
            'solutions.created AS created, s_question AS s_question' \
            % (username, then, username, then)
        news = []
        res, _ = db.cypher_query(query)
        # Profiled with ~50 objects and it was still performing under 1 ms.
        # By the time sorting in python becomes an issue the above mentioned
        # ticket should be resolved.
        res = sorted(res, key=attrgetter('created'), reverse=True)[:5]
        page = api.paginate_queryset(res)
        for row in page:
            news_article = None
            if row.questions is not None:
                row.questions.pull()
                news_article = QuestionSerializerNeo(
                    Question.inflate(row.questions),
                    context={'request': request}).data
            elif row.solutions is not None:
                row.s_question.pull()
                row.solutions.pull()
                question_data = QuestionSerializerNeo(
                    Question.inflate(row.s_question)).data
                news_article = SolutionSerializerNeo(
                    Solution.inflate(row.solutions),
                    context={'request': request}).data
                news_article['question'] = question_data
            news.append(news_article)
        return api.get_paginated_response(news)


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
        [row[0].pull() for row in res]
        return [Address.inflate(row[0]) for row in res]

    def get_object(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address {object_uuid: "%s"}) RETURN b' % (
                    self.request.user.username, self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return Address.inflate(res[0][0])


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
    permission_classes = (IsAnonCreateReadOnlyOrIsAuthenticated, )

    def get_object(self):
        return Pleb.get(self.kwargs[self.lookup_field])

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = Pleb.get(username=request.user.username, cache_buster=True)
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

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
        query = 'MATCH (a:Pleb {username: "%s"})<-[:OWNED_BY]-' \
                '(b:Question) WHERE b.to_be_deleted=false' \
                ' %s RETURN b' % (username, additional_params)
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
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
        [row[0].pull() for row in res]
        queryset = [SBContent.inflate(row[0]) for row in res]

        page = self.paginate_queryset(queryset)
        serializer = MarkdownContentSerializer(page, many=True,
                                               context={'request': request})
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'])
    def public(self, request, username=None):
        return get_public_content(self, username, request)

    @detail_route(methods=['post'],
                  permission_classes=(IsAuthenticated, IsSelfOrReadOnly))
    def follow(self, request, username=None):
        """
        This endpoint allows users to follow other users.
        :param username:
        :param request:
        """
        queryset = self.get_object()
        is_following = queryset.is_following(request.user.username)
        if is_following:
            return Response({"detail": "Already following user.",
                             "status": status.HTTP_200_OK},
                            status=status.HTTP_200_OK)
        queryset.follow(request.user.username)
        return Response({"detail": "Successfully followed user.",
                         "status": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated,))
    def followers(self, request, username=None):
        query = 'MATCH (p:Pleb {username:"%s"})<-[r:FOLLOWING]-' \
                '(followers:Pleb) WHERE r.active ' \
                'RETURN followers' % username
        res, _ = db.cypher_query(query)
        if res.one:
            follower_list = [Pleb.inflate(row[0]) for row in res]
            return self.get_paginated_response(self.paginate_queryset(
                PlebSerializerNeo(follower_list, many=True).data))
        return self.get_paginated_response(self.paginate_queryset([]))

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticated,))
    def following(self, request, username=None):
        query = 'MATCH (p:Pleb {username:"%s"})-[r:FOLLOWING]->' \
                '(followers:Pleb) WHERE r.active ' \
                'RETURN followers' % username
        res, _ = db.cypher_query(query)
        if res.one:
            follower_list = [Pleb.inflate(row[0]) for row in res]
            return self.get_paginated_response(self.paginate_queryset(
                PlebSerializerNeo(follower_list, many=True).data))
        return self.get_paginated_response(self.paginate_queryset([]))

    @detail_route(methods=['post'],
                  permission_classes=(IsAuthenticated, IsSelfOrReadOnly))
    def unfollow(self, request, username=None):
        """
        This endpoint allows users to unfollow other users.
        :param username:
        :param request:
        """
        queryset = self.get_object()
        is_following = queryset.is_following(request.user.username)
        if not is_following:
            return Response({"detail": "Already not following user.",
                             "status": status.HTTP_200_OK},
                            status=status.HTTP_200_OK)
        queryset.unfollow(request.user.username)
        return Response({"detail": "Successfully unfollowed user.",
                         "status": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)

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
        # Added in the ORDER BY to ensure order for the infinite scroll
        # loading on a users friend list page
        query = 'MATCH (a:Pleb {username: "%s"})-' \
                '[:FRIENDS_WITH {active: true}]->' \
                '(b:Pleb) RETURN DISTINCT b ORDER BY b.first_name' % username
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
        queryset = [Pleb.inflate(row[0]) for row in res]
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, ))
    def reputation(self, request, username=None):
        user = self.get_object()
        return Response({"reputation": user.reputation,
                         "reputation_change":
                             user.reputation_change},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, ))
    def senators(self, request, username=None):
        # TODO this may be able to be refined to [:REPRESENTED_BY]->(s:Senator)
        senators = cache.get("%s_senators" % username)
        if senators is None:
            query = "MATCH (a:Pleb {username: '%s'})-[:HAS_SENATOR]->" \
                    "(s:PublicOfficial) RETURN s" % username
            res, col = db.cypher_query(query)
            [row[0].pull() for row in res]
            senators = [PublicOfficial.inflate(row[0]) for row in res]
            cache.set("%s_senators" % username, senators, timeout=1800)
        if len(senators) == 0:
            return Response([], status=status.HTTP_200_OK)
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
                cache.set("%s_house_representative" % username, house_rep,
                          timeout=1800)
            except IndexError:
                return Response({}, status=status.HTTP_200_OK)
        return Response(PublicOfficialSerializer(house_rep).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def president(self, request, username=None):
        president = cache.get("%s_president" % username)
        if president is None:
            query = 'MATCH (p:Pleb {username:"%s"})-[:HAS_PRESIDENT]->' \
                    '(o:PublicOfficial) RETURN o' % username
            res, _ = db.cypher_query(query)
            try:
                president = PublicOfficial.inflate(res[0][0])
                cache.set("%s_president" % username, president, timeout=1800)
            except IndexError:
                return Response({}, status=status.HTTP_200_OK)
        return Response(PublicOfficialSerializer(president).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def is_beta_user(self, request, username=None):
        return Response({'is_beta_user': self.get_object().is_beta_user()},
                        status.HTTP_200_OK)

    @detail_route(methods=['get'],
                  permission_classes=(IsAuthenticatedOrReadOnly,))
    def missions(self, request, username):
        query = 'MATCH (quest:Quest {owner_username: "%s"})-' \
                '[:EMBARKS_ON]->(m:Mission) RETURN m' % username
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        queryset = [Mission.inflate(row[0]) for row in res]
        page = self.paginate_queryset(queryset)
        serializer = MissionSerializer(page, many=True,
                                       context={'request': request})
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=["GET"], serializer_class=MissionSerializer,
                  permission_classes=(IsAuthenticated,))
    def endorsed(self, request, username):
        query = 'MATCH (p:Pleb {username:"%s"})-' \
                '[:ENDORSES]->(m:Mission) RETURN m' % username
        res, _ = db.cypher_query(query)
        page = self.paginate_queryset(
            [Mission.inflate(mission[0]) for mission in res])
        serializer = self.serializer_class(page, many=True,
                                           context={'request': request})
        return self.get_paginated_response(serializer.data)


class MeViewSet(mixins.UpdateModelMixin,
                mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This endpoint provides the ability to get information regarding the
    currently authenticated user. This way AJAX, Ember, and other front end
    systems don't need to know what username they should bake into a
    /profile/ url to get information on the signed in user.
    """
    serializer_class = PlebSerializerNeo
    permission_classes = (IsAuthenticated, IsSelf)

    def get_object(self):
        return Pleb.get(self.request.user.username)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = Pleb.get(username=request.user.username, cache_buster=True)
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = dict(serializer.data)
        return Response(serializer_data, status=status.HTTP_200_OK)

    @list_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def public(self, request):
        return get_public_content(self, request.user.username, request)

    @list_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def newsfeed(self, request):
        """
        The newsfeed endpoint expects to be called on the me endpoint and
        assumes that the request object provided will contain the user the
        newsfeed is being provided to. It is not included as a list_route on
        the me endpoint due to the me endpoint not being a viewset.
        If we transition to that structure it could easily be moved to a
        list_route there.
        Query if we want to grab tags:
        MATCH (a:Pleb {username: "%s"})-
                [OWNS_QUESTION]->(questions:Question)-[:TAGGED_AS]->(tags:Tag)
            WHERE questions.to_be_deleted = False AND questions.created > %s
            RETURN questions, tags.name AS tags, NULL as solutions,
                NULL as posts UNION
        MATCH (a)-[manyFriends:FRIENDS_WITH*2 {active: True}]->
                ()-[OWNS_QUESTION]->(questions:Question)-[:TAGGED_AS]->
                (tags:Tag)
            WHERE questions.to_be_deleted = False AND questions.created > %s
            RETURN questions, tags.name AS tags, NULL as posts,
                NULL as solutions UNION

        :param request:
        """
        # This query retrieves all of the current user's posts, solutions,
        # and questions as well as their direct friends posts, solutions,
        # and questions. It then looks for all of their friends friends
        # solutions and questions, combines all of the content and
        # returns the result. The query filters out content scheduled for
        # deletion and only looks for content created more recently than the
        # time provided. The reasoning for not including friends of friends
        # posts is to try and improve privacy. Friends of friends have not
        # actually been accepted potentially as friends by the user and
        # therefore should not have access to information posted on the user's
        # wall which in this case would be their posts.
        # We currently do not sort this query in neo because we are waiting
        # for post processing on unions as a whole to be added as a feature.
        # See Github issue #2725 for updates
        # https://github.com/neo4j/neo4j/issues/2725
        then = (datetime.now(pytz.utc) - timedelta(days=120)).strftime("%s")
        query = \
            '// Retrieve all the current users questions\n' \
            'MATCH (a:Pleb {username: "%s"})<-[:OWNED_BY]-' \
            '(questions:Question) ' \
            'WHERE questions.to_be_deleted = False AND questions.created > %s' \
            ' AND questions.is_closed = False ' \
            'RETURN questions, NULL AS solutions, NULL AS posts, ' \
            'questions.created AS created, NULL AS s_question, ' \
            'NULL AS mission, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve all the news articles the user may be \n' \
            '// interested in\n' \
            'MATCH (a:Pleb {username: "%s"})-[:INTERESTED_IN]->' \
            '(tag:Tag)<-[:TAGGED_AS]-(news:NewsArticle) ' \
            'WHERE news.published > %s AND news.is_closed = False ' \
            ' RETURN DISTINCT news, NULL AS solutions, NULL AS posts, ' \
            'news.published AS created, NULL AS s_question, ' \
            'NULL AS mission, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS questions UNION ' \
            '' \
            '// Retrieve all the current users solutions\n' \
            'MATCH (a:Pleb {username: "%s"})<-' \
            '[:OWNED_BY]-(solutions:Solution)<-' \
            '[:POSSIBLE_ANSWER]-(s_question:Question) ' \
            'WHERE s_question.to_be_deleted = False ' \
            'AND solutions.created > %s' \
            ' AND solutions.is_closed = False ' \
            'AND s_question.is_closed = False ' \
            'RETURN solutions, NULL AS questions, NULL AS posts, ' \
            'solutions.created AS created, s_question AS s_question,' \
            'NULL AS mission, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve all the current users posts\n' \
            'MATCH (a:Pleb {username: "%s"})<-[:OWNED_BY]-(posts:Post) ' \
            'WHERE posts.to_be_deleted = False AND posts.created > %s ' \
            'AND posts.is_closed = False ' \
            'RETURN posts, NULL as questions, NULL as solutions, ' \
            'posts.created AS created, NULL AS s_question,' \
            'NULL AS mission, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve all the posts on the current users wall that are \n' \
            '// not owned by the current user \n' \
            'MATCH (a:Pleb {username: "%s"})-[:OWNS_WALL]->(w:Wall)' \
            '-[:HAS_POST]->(posts:Post) ' \
            'WHERE NOT (posts)-[:OWNED_BY]->(a) AND ' \
            'posts.to_be_deleted = False AND posts.created > %s ' \
            'AND posts.is_closed = False ' \
            'RETURN posts, NULL as questions, NULL as solutions, ' \
            'posts.created AS created, NULL AS s_question,' \
            'NULL AS mission, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve the missions affecting the given user\n' \
            'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->(:Address)-' \
            '[:ENCOMPASSED_BY*..]->' \
            '(:Location)<-[:WITHIN]-(mission:Mission {active: true})' \
            '<-[:EMBARKS_ON]-(quest:Quest {active: true}) ' \
            'WHERE NOT((mission)-[:FOCUSED_ON]->(:Position {verified:false}))' \
            ' AND mission.created > %s ' \
            'RETURN mission, NULL AS solutions, NULL AS posts, ' \
            'NULL AS questions, mission.created AS created, ' \
            'NULL AS s_question, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve the mission updates affecting ' \
            '// the given user\n' \
            'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->(:Address)-' \
            '[:ENCOMPASSED_BY*..]->' \
            '(:Location)<-[:WITHIN]-(q_mission:Mission {active: true})' \
            '<-[:EMBARKS_ON]-(quest:Quest {active: true}) WITH q_mission ' \
            'MATCH (q_mission)<-[:ABOUT]-(updates:Update) ' \
            'WHERE NOT((q_mission)-[:FOCUSED_ON]' \
            '->(:Position {verified:false}))' \
            ' AND updates.created > %s AND updates.is_closed = False ' \
            'RETURN updates, NULL AS solutions, NULL AS posts, ' \
            'NULL AS questions, updates.created AS created, ' \
            'NULL AS s_question, NULL as mission, q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            "// Retrieve all the current user's friends posts on their \n" \
            '// walls\n' \
            'MATCH (a:Pleb {username: "%s"})-' \
            '[r:FRIENDS_WITH {active: True}]->(p:Pleb)<-' \
            '[:OWNED_BY]-(posts:Post) ' \
            'WHERE (posts)-[:POSTED_ON]->(:Wall)<-[:OWNS_WALL]-(p) AND ' \
            'HAS(r.active) AND posts.to_be_deleted = False ' \
            'AND posts.created > %s AND posts.is_closed = False ' \
            'RETURN posts, NULL AS questions, NULL AS solutions, ' \
            'posts.created AS created, NULL AS s_question, ' \
            'NULL AS mission, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve all the current users friends and friends of friends' \
            '// questions \n' \
            'MATCH (a:Pleb {username: "%s"})-' \
            '[manyFriends:FRIENDS_WITH*..2 {active: True}]' \
            '->(:Pleb)<-[:OWNED_BY]-(questions:Question) ' \
            'WHERE questions.to_be_deleted = False AND ' \
            'questions.created > %s AND questions.is_closed = False ' \
            'RETURN questions, NULL AS posts, NULL AS solutions, ' \
            'questions.created AS created, NULL AS s_question, ' \
            'NULL AS mission, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve all the current users friends and friends of friends' \
            '// solutions \n' \
            'MATCH (a:Pleb {username: "%s"})-' \
            '[manyFriends:FRIENDS_WITH*..2 {active: True}]->' \
            '(:Pleb)<-[:OWNED_BY]-' \
            '(solutions:Solution)<-[:POSSIBLE_ANSWER]-' \
            '(s_question:Question) ' \
            'WHERE solutions.to_be_deleted = False AND solutions.created > %s' \
            ' AND solutions.is_closed = False ' \
            'AND s_question.is_closed = False ' \
            'RETURN solutions, NULL AS posts, NULL AS questions, ' \
            'solutions.created AS created, s_question AS s_question,' \
            'NULL AS mission, NULL AS updates, NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve all the users questions that the current user is ' \
            '// following \n' \
            'MATCH (a:Pleb {username: "%s"})-[r:FOLLOWING {active: True}]->' \
            '(:Pleb)<-[:OWNED_BY]-(questions:Question) ' \
            'WHERE questions.to_be_deleted = False AND ' \
            'questions.created > %s AND questions.is_closed = False ' \
            'RETURN NULL AS solutions, NULL AS posts, ' \
            'questions AS questions, questions.created AS created, ' \
            'NULL AS s_question, NULL AS mission, NULL AS updates, ' \
            'NULL AS q_mission, ' \
            'NULL AS news UNION ' \
            '' \
            '// Retrieve all the users solutions that the current user is ' \
            '// following \n' \
            'MATCH (a:Pleb {username: "%s"})-[r:FOLLOWING {active: True}]->' \
            '(:Pleb)<-[:OWNED_BY]-(solutions:Solution)<-' \
            '[:POSSIBLE_ANSWER]-(s_question:Question) ' \
            'WHERE s_question.to_be_deleted = False AND ' \
            'solutions.created > %s AND solutions.is_closed = False ' \
            'RETURN solutions, NULL AS posts, ' \
            'NULL AS questions, solutions.created AS created, ' \
            's_question as s_question, NULL AS mission, NULL AS updates, ' \
            'NULL AS q_mission, ' \
            'NULL AS news' \
            % (
                request.user.username, then, request.user.username, then,
                request.user.username, then, request.user.username, then,
                request.user.username, then, request.user.username, then,
                request.user.username, then, request.user.username, then,
                request.user.username, then, request.user.username, then,
                request.user.username, then, request.user.username, then)
        news = []
        res, _ = db.cypher_query(query)
        # Profiled with ~50 objects and it was still performing under 1 ms.
        # By the time sorting in python becomes an issue the above mentioned
        # ticket should be resolved.
        res = sorted(res, key=attrgetter('created'), reverse=True)
        page = self.paginate_queryset(res)
        for row in page:
            news_article = None
            if row.questions is not None:
                row.questions.pull()
                news_article = QuestionSerializerNeo(
                    Question.inflate(row.questions),
                    context={'request': request}).data
            elif row.solutions is not None:
                row.s_question.pull()
                row.solutions.pull()
                question_data = QuestionSerializerNeo(
                    Question.inflate(row.s_question)).data
                news_article = SolutionSerializerNeo(
                    Solution.inflate(row.solutions),
                    context={'request': request}).data
                news_article['question'] = question_data
            elif row.posts is not None:
                row.posts.pull()
                news_article = PostSerializerNeo(
                    Post.inflate(row.posts),
                    context={'request': request}).data
            elif row.mission is not None:
                row.mission.pull()
                news_article = MissionSerializer(
                    Mission.inflate(row.mission),
                    context={'request': request}).data
                news_article['reputation'] = Pleb.get(
                    username=news_article['owner_username']).reputation
            elif row.updates is not None:
                row.updates.pull()
                row.q_mission.pull()
                news_article = UpdateSerializer(
                    Update.inflate(row.updates),
                    context={'request': request}).data
                news_article['mission'] = MissionSerializer(
                    Mission.inflate(row.q_mission),
                    context={'request': request}).data
            elif row.news is not None:
                row.news.pull()
                news_article = NewsArticleSerializer(
                    NewsArticle.inflate(row.news),
                    context={'request': request}).data
            news.append(news_article)
        return self.get_paginated_response(news)

    @list_route(methods=['get'], serializer_class=DonationSerializer,
                permission_classes=(IsAuthenticated,))
    def donations(self, request):
        query = 'MATCH (a:Pleb {username:"%s"})-[:DONATIONS_GIVEN]->' \
                '(d:Donation)-[:CONTRIBUTED_TO]->(:Mission) ' \
                'RETURN d ORDER BY d.created DESC' % \
                request.user.username
        res, _ = db.cypher_query(query)
        queryset = [Donation.inflate(row[0]) for row in res]
        html = self.request.query_params.get('html', 'false')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         context={'request': request})
        if html == 'true':
            html_array = []
            for item in serializer.data:
                context = RequestContext(request, item)
                html_array.append(render_to_string(
                    "settings/donation_block.html",
                    context))
            return self.get_paginated_response(html_array)
        return self.get_paginated_response(serializer.data)

    @list_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def payment_methods(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        pleb = Pleb.get(username=request.user.username)
        cards = []
        if pleb.stripe_customer_id is not None:
            account = stripe.Customer.retrieve(pleb.stripe_customer_id)
            for card in account.sources.data:
                cards.append({
                    "id": card.id,
                    "brand": card.brand,
                    "exp_month": card.exp_month,
                    "exp_year": card.exp_year,
                    "last4": card.last4,
                    "default":
                        True
                        if card.id == pleb.stripe_default_card_id else False,
                })
        return Response({
            "count": len(cards),
            "next": None,
            "previous": None,
            "results": cards
        }, status=status.HTTP_200_OK)

    @list_route(methods=['post'], serializer_class=PoliticalPartySerializer,
                permission_classes=(IsAuthenticated,))
    def add_parties(self, request):
        """
        Connects the authenticated pleb up to all the existing parties that
        are passed within a list. Returns all of names of the successfully
        connected parties.
        """
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            added = []
            for party in serializer.data['names']:
                query = 'MATCH (a:PoliticalParty {name: "%s"}), ' \
                        '(b:Pleb {username: "%s"}) ' \
                        'CREATE UNIQUE (a)<-[r:AFFILIATES_WITH]-(b) ' \
                        'RETURN r' % (party, request.user.username)
                res, _ = db.cypher_query(query)
                if res.one:
                    added.append(party)
            response = serializer.data
            response['names'] = added
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], serializer_class=InterestsSerializer,
                permission_classes=(IsAuthenticated,))
    def add_interests(self, request):
        """
        Connects the authenticated pleb up to all the existing parties that
        are passed within a list. Returns all of names of the successfully
        connected parties.
        :param request:
        """
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            added = []
            for interest in serializer.data['interests']:
                query = 'MATCH (a:ActivityInterest {name: "%s"}), ' \
                        '(b:Pleb {username: "%s"}) ' \
                        'CREATE UNIQUE (a)<-[r:WILL_PARTICIPATE]-(b) ' \
                        'RETURN r' % (interest, request.user.username)
                res, _ = db.cypher_query(query)
                if res.one:
                    added.append(interest)
            response = serializer.data
            response['interests'] = added
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SentFriendRequestViewSet(viewsets.ModelViewSet):
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
                                    self.request.user.username)
        if friend_requests is None:
            filter_by = self.request.query_params.get("filter", "")
            filtered = get_filter_by(filter_by)
            query = "MATCH (p:Pleb {username:'%s'})-%s-(" \
                    "r:FriendRequest) RETURN distinct r" \
                    % (self.request.user.username, filtered)
            res, col = db.cypher_query(query)
            friend_requests = [FriendRequest.inflate(row[0]) for row in res]
            cache.set("%s_friend_requests" % self.request.user.username,
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
        profile = Pleb.get(username=request.user.username, cache_buster=True)
        # TODO: Change this to modifying the relationship manager rather than
        # just disconnecting

        profile.friends.disconnect(friend)
        friend.friends.disconnect(profile)
        cache.delete(profile.username)
        return Response({'detail': 'success'},
                        status=status.HTTP_204_NO_CONTENT)


class FriendRequestList(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This endpoint assumes it is placed on a specific user endpoint where
    it can rely on the currently logged in user to gather notifications
    for. It is not capable of being set on an arbitrary user's profile
    endpoint like other method endpoints we have.
    """
    serializer_class = FriendRequestSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:RECEIVED_A_REQUEST]->' \
                '(n:FriendRequest) RETURN n ORDER ' \
                'BY n.created DESC LIMIT 5' % self.request.user.username
        res, col = db.cypher_query(query)
        return [FriendRequest.inflate(row[0]) for row in res]

    def list(self, request, *args, **kwargs):
        """
        Had to overwrite this function to add a check for a query param being
        passed that when set to true will set all the user's current
        notifications to seen
        :param request:
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

    @detail_route(methods=['post'], permission_classes=(IsAuthenticated, ))
    def accept(self, request, object_uuid=None):
        query = "MATCH (from_pleb:Pleb)<-[:REQUEST_FROM]-" \
                "(friend_request:FriendRequest {object_uuid: '%s'})" \
                "-[:REQUEST_TO]->(to_pleb:Pleb) " \
                "RETURN from_pleb, to_pleb, friend_request" % object_uuid
        res, _ = db.cypher_query(query)
        if res.one is None:
            return Response({
                'detail': 'Sorry this object does not exist.',
                "status": status.HTTP_404_NOT_FOUND,
                "developer_message":
                    "It doesn't look that the ID that was provided"
                    "was a valid object in our database. If "
                    "you believe this is incorrect please reach"
                    " out to us through our email at"
                    " developers@sagebrew.com"
            }, status=status.HTTP_404_NOT_FOUND)
        to_pleb = Pleb.inflate(res.one.from_pleb)
        from_pleb = Pleb.inflate(res.one.to_pleb)
        if from_pleb not in to_pleb.friends:
            to_pleb.friends.connect(from_pleb)
        if to_pleb not in from_pleb.friends:
            from_pleb.friends.connect(to_pleb)
        FriendRequest.inflate(res.one.friend_request).delete()
        return Response({
            'detail': 'Successfully accepted friend request.',
            "status": status.HTTP_200_OK,
            "developer_message": ""
        }, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], permission_classes=(IsAuthenticated, ))
    def decline(self, request, object_uuid=None):
        friend_request = FriendRequest.nodes.get(object_uuid=object_uuid)
        friend_request.delete()
        return Response({
            'detail': 'Successfully declined friend request.',
            "status": status.HTTP_200_OK,
            "developer_message": ""
        }, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], permission_classes=(IsAuthenticated, ))
    def block(self, request, object_uuid=None):
        friend_request = FriendRequest.nodes.get(object_uuid=object_uuid)
        friend_request.seen = True
        friend_request.response = 'block'
        friend_request.save()
        return Response({
            'detail': 'Successfully blocked further friend requests.',
            "status": status.HTTP_200_OK,
            "developer_message": ""
        }, status=status.HTTP_200_OK)

    @list_route(permission_classes=(IsAuthenticated, ))
    def render(self, request, object_uuid=None):
        """
        This is a intermediate step on the way to utilizing a JS Framework to
        handle template rendering.
        :param request:
        :param object_uuid:
        """
        html_array = []
        id_array = []
        notifications = self.list(request)
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
