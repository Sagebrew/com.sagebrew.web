from dateutil import parser
from operator import attrgetter

from django.template.loader import render_to_string

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated

from neomodel import db

from sb_base.neo_models import SBContent
from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_posts.neo_models import Post
from sb_comments.neo_models import Comment
from sb_questions.serializers import QuestionSerializerNeo
from sb_solutions.serializers import SolutionSerializerNeo
from sb_comments.serializers import CommentSerializer
from sb_posts.serializers import PostSerializerNeo
from sb_quests.neo_models import Position
from sb_quests.serializers import PositionSerializer
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer

from .serializers import CouncilVoteSerializer


class CouncilObjectEndpoint(viewsets.ModelViewSet):
    serializer_class = CouncilVoteSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return SBContent.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_update(self, serializer):
        serializer.save(pleb=Pleb.get(self.request.user.username))

    def get_filter(self):
        vote_filter = self.request.query_params.get('filter', '').lower()
        if vote_filter == 'voted':
            return ''
        else:
            return 'NOT'

    def get_queryset(self):
        """
        This query gets all objects which are flagged and either not voted on
        by the user visiting the page or where they have voted by deactivated
        their vote.

        :return:
        """
        vote_filter = self.get_filter()
        query = '// Retrieve all questions which have been flagged\n' \
                'MATCH (content:Question)-[HAS_FLAG]->(f:Flag) ' \
                'WITH content MATCH content WHERE %s ' \
                '(content)-[:COUNCIL_VOTE {active:true}]->' \
                '(:Pleb {username:"%s"}) AND ' \
                'content.to_be_deleted=False AND content.visibility="public" ' \
                'RETURN content as questions, NULL as solutions, ' \
                'content.created as created, ' \
                'NULL as posts, NULL as comments UNION MATCH ' \
                '' \
                '// Retrieve all solutions which have been flagged\n' \
                '(content:Solution)-[HAS_FLAG]->(f:Flag) ' \
                'WITH content MATCH content WHERE %s ' \
                '(content)-[:COUNCIL_VOTE {active:true}]->' \
                '(:Pleb {username:"%s"}) AND ' \
                'content.to_be_deleted=False and content.visibility="public" ' \
                'RETURN NULL as questions, content as solutions, ' \
                'content.created as created, ' \
                'NULL as posts, NULL as comments ' \
                '' \
                '// Retrieve all comments which have been flagged\n' \
                'UNION MATCH (content:Comment)-[HAS_FLAG]->(f:Flag) ' \
                'WITH content MATCH content WHERE %s ' \
                '(content)-[:COUNCIL_VOTE {active:true}]->' \
                '(:Pleb {username:"%s"}) AND ' \
                'content.to_be_deleted=False and content.visibility="public" ' \
                'RETURN NULL as questions, content as comments, ' \
                'content.created as created, ' \
                'NULL as posts, NULL as solutions ' \
                '' \
                '// Retrieve all posts which have been flagged\n' \
                'UNION MATCH (content:Post)-[HAS_FLAG]->(f:Flag) ' \
                'WITH content MATCH content WHERE %s ' \
                '(content)-[:COUNCIL_VOTE {active:true}]->' \
                '(:Pleb {username:"%s"}) AND ' \
                'content.to_be_deleted=False and content.visibility="public" ' \
                'RETURN NULL as questions, content as posts, ' \
                'content.created as created, ' \
                'NULL as comments, NULL as solutions' % \
                (vote_filter, self.request.user.username, vote_filter,
                 self.request.user.username, vote_filter,
                 self.request.user.username, vote_filter,
                 self.request.user.username)
        res, _ = db.cypher_query(query)
        res = sorted(res, key=attrgetter('created'), reverse=True)
        return res

    def list(self, request, *args, **kwargs):
        council_list = []
        html = request.query_params.get('html', 'false').lower()
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        for row in page:
            if row[0] is not None:
                row[0].pull()  # fix for None objects being returned
                # from the query due to multiple column returns
            council_object = None
            if row.questions is not None:
                council_object = QuestionSerializerNeo(
                    Question.inflate(row.questions),
                    context={'request': request}).data
            elif row.solutions is not None:
                council_object = SolutionSerializerNeo(
                    Solution.inflate(row.solutions),
                    context={'request': request}).data
            elif row.comments is not None:
                council_object = CommentSerializer(
                    Comment.inflate(row.comments),
                    context={'request': request}).data
            elif row.posts is not None:
                council_object = PostSerializerNeo(
                    Post.inflate(row.posts),
                    context={'request': request}).data
            if html == 'true':
                council_object['last_edited_on'] = parser.parse(
                    council_object['last_edited_on'])
                council_object['request'] = request
                council_object = {
                    "html": render_to_string("council_votable.html",
                                             council_object),
                    "id": council_object["id"],
                    "type": council_object["type"]
                }
            council_list.append(council_object)
        return self.get_paginated_response(council_list)

    @list_route(serializer_class=PositionSerializer,
                permission_classes=(IsAuthenticated,))
    def positions(self, request):
        query = 'MATCH (p:Position {verified: false}) RETURN p'
        res, _ = db.cypher_query(query)
        return Response(
            [PositionSerializer(Position.inflate(row[0])).data
             for row in res], status=status.HTTP_200_OK)

    @list_route(serializer_class=MissionSerializer,
                    permission_classes=(IsAuthenticated,))
    def missions(self, request):
        query = 'MATCH (m:Mission)<-[:EMBARKS_ON]-(:Quest) RETURN m'
        res, _ = db.cypher_query(query)
        return Response(
            [self.get_serializer(Mission.inflate(row[0])).data
             for row in res], status=status.HTTP_200_OK)
