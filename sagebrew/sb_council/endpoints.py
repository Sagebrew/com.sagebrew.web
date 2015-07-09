from datetime import datetime
from dateutil import parser
from logging import getLogger
from operator import attrgetter

from django.core.cache import cache
from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from neomodel import db

from sb_base.neo_models import SBContent
from sb_base.views import ObjectRetrieveUpdateDestroy
from sb_base.serializers import SBSerializer
from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_posts.neo_models import Post
from sb_comments.neo_models import Comment
from sb_questions.serializers import QuestionSerializerNeo
from sb_solutions.serializers import SolutionSerializerNeo
from sb_comments.serializers import CommentSerializer
from sb_posts.serializers import PostSerializerNeo
from sb_flags.neo_models import Flag
from sb_flags.serializers import FlagSerializer

from .serializers import CouncilVoteSerializer

logger = getLogger('loggly_logs')


class CouncilObjectEndpoint(viewsets.ModelViewSet):
    serializer_class = CouncilVoteSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return SBContent.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_update(self, serializer):
        serializer.save(pleb=Pleb.get(self.request.user.username))

    def get_queryset(self):
        query = 'MATCH (questions:Question)-[HAS_FLAG]->(f:Flag) ' \
                'WHERE questions.to_be_deleted=False and questions.visibility="public" RETURN questions, ' \
                'NULL as solutions, NULL as posts, NULL as comments ' \
                'UNION MATCH (solutions:Solution)-[HAS_FLAG]->(f:Flag) ' \
                'WHERE solutions.to_be_deleted=False and solutions.visibility="public" RETURN ' \
                'NULL as questions, ' \
                'solutions, NULL as posts, NULL as comments ' \
                'UNION MATCH (comments:Comment)-[HAS_FLAG]->(f:Flag) ' \
                'WHERE comments.to_be_deleted=false and comments.visibility="public" RETURN ' \
                'NULL as questions, ' \
                'NULL as solutions, NULL as posts, comments ' \
                'UNION MATCH (posts:Post)-[HAS_FLAG]->(f:Flag) WHERE ' \
                'posts.to_be_deleted=false and posts.visibility="public" RETURN NULL as questions, ' \
                'NULL as solutions, posts, NULL as comments'
        res, _ = db.cypher_query(query)
        return res

    def list(self, request, *args, **kwargs):
        council_list = []
        html = request.query_params.get('html', 'false')
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        for row in page:
            council_object = None
            if row.questions is not None:
                council_object = QuestionSerializerNeo(
                    Question.inflate(row.questions),
                    context={'request':request}).data
            if row.solutions is not None:
                council_object = SolutionSerializerNeo(
                    Solution.inflate(row.solutions),
                    context={'request': request}).data
            if row.comments is not None:
                council_object = CommentSerializer(
                    Comment.inflate(row.comments),
                    context={'request': request}).data
            if row.posts is not None:
                council_object = PostSerializerNeo(
                    Post.inflate(row.posts),
                    context={'request': request}).data
            if html == 'true':
                council_object['last_edited_on'] = parser.parse(
                    council_object['last_edited_on'])
                council_object = {
                    "html": render_to_string("council_votable.html",
                                             council_object),
                    "id": council_object["id"],
                    "type": council_object["type"]
                }
            council_list.append(council_object)
        return self.get_paginated_response(council_list)
