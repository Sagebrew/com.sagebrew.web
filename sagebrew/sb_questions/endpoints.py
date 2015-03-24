from uuid import uuid1
from datetime import datetime
import pytz
from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination

from neomodel import CypherException

from sagebrew import errors

from api.utils import request_to_api
from sb_docstore.utils import (get_dynamo_table, convert_dynamo_content)
from sb_solutions.utils import convert_dynamo_solutions
from sb_comments.serializers import CommentSerializer
from sb_comments.utils import convert_dynamo_comments


from .serializers import QuestionSerializerNeo
from .neo_models import SBQuestion
from .utils import clean_question_for_rest


logger = getLogger('loggly_logs')


class QuestionViewSet(viewsets.GenericViewSet):
    serializer_class = QuestionSerializerNeo
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        try:
            queryset = SBQuestion.nodes.all()
        except(CypherException, IOError):
            logger.exception("QuestionGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        sort_by = self.request.QUERY_PARAMS.get('sort_by', None)
        if sort_by == "created":
            queryset = sorted(queryset, key=lambda k: k.created)
        elif sort_by == "edited":
            queryset = sorted(queryset, key=lambda k: k.last_edited_on)
        else:
            queryset = sorted(queryset, key=lambda k: k.get_vote_count())
        return queryset

    def get_object(self, object_uuid=None):
        try:
            queryset = SBQuestion.nodes.get(object_uuid=object_uuid)
        except(CypherException, IOError):
            logger.exception("QuestionViewSet queryset")
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

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            instance = self.serializer_class(instance)
            return Response(instance.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, object_uuid=None):
        table = get_dynamo_table("public_questions")
        if isinstance(table, Exception) is True:
            logger.exception("QuestionsViewSet get_object")
            return Response(errors.DYNAMO_TABLE_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        queryset = table.get_item(object_uuid=object_uuid)

        expand = self.request.QUERY_PARAMS.get('expand', "false").lower()
        try:
            if expand == "false":
                single_object = convert_dynamo_content(queryset)
            else:
                single_object = convert_dynamo_content(queryset, self.request,
                                                       "question-comments")
        except IndexError as e:
            raise NotFound
        # TODO need to just store username for question and solution, can
        # determine url paths dynamically here
        user_url = reverse('user-detail', kwargs={
            'username': single_object["owner_profile_url"]}, request=request)
        single_object["profile_url"] = reverse(
            'profile_page', kwargs={
                'pleb_username': single_object["owner_profile_url"]
            }, request=request)

        # TODO hopefully can clear out most of this and just use it to eliminate
        # any data only used for server side logic
        single_object = clean_question_for_rest(single_object)

        if expand == "false":
            single_object["owner"] = user_url
            single_object["comments"] = reverse(
                "question-comments", kwargs={'object_uuid': object_uuid},
                request=request)
        else:
            response = request_to_api(user_url, request.user.username,
                                      req_method="GET")
            single_object["owner"] = response.json()

        return Response(single_object, status=status.HTTP_200_OK)

    def update(self, request, object_uuid=None):
        pass

    def partial_update(self, request, object_uuid=None):
        pass

    def destroy(self, request, object_uuid=None):
        pass

    @detail_route(methods=['get'])
    def solutions(self, request, object_uuid=None):
        table = get_dynamo_table("public_solutions")
        if isinstance(table, Exception) is True:
            logger.exception("QuestionsViewSet solutions")
            return Response(errors.DYNAMO_TABLE_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        queryset = table.query_2(parent_object__eq=object_uuid)
        queryset = convert_dynamo_solutions(queryset, self.request)
        sort_by = self.request.QUERY_PARAMS.get('sort_by', None)
        if sort_by == "created":
            queryset = sorted(
                queryset,
                key=lambda k: k['created'])
        elif sort_by == "edited":
            queryset = sorted(
                queryset,
                key=lambda k: k['last_edited_on'])
        else:
            queryset = sorted(queryset, key=lambda k: k['vote_count'])
        # TODO probably want to replace with a serializer if we want to get
        # any urls returned. Or these could be stored off into dynamo based on
        # the initial pass on the serializer
        return Response(queryset, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], serializer_class=CommentSerializer)
    def comments(self, request, object_uuid=None):
        # TODO should be able to move all this to comment helpers and
        # place in solutions, posts, questions, etc.
        table = get_dynamo_table("comments")
        if isinstance(table, Exception) is True:
            logger.exception("QuestionGenericViewSet comment")
            return Response(errors.DYNAMO_TABLE_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if request.method == "GET":
            queryset = table.query_2(
                parent_object__eq=object_uuid,
                created__gte="0"
            )
            serializer = CommentSerializer(
                convert_dynamo_comments(queryset), context={"request": request},
                many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # TODO should be able to move all this to comment helpers and
            # place in solutions, posts, questions, etc.
            parent_uuid = object_uuid
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                # TODO should probably spawn neo connection off into task
                # and instead make relation in dynamo. Can include the given
                # uuid in the task spawned off. Also as mentioned in the
                # serializer, we should capture the user from the request,
                # get the pleb (maybe in the task) and use that to call
                # comment_relations
                instance = serializer.save()
                parent_object = self.get_object(object_uuid)
                parent_object.comments.connect(instance)
                parent_object.save()
                # TODO should really define this in CommentSerializerDynamo
                # and require all these as inputs or dynamically generated
                # and then pass the necessary additional attributes on along
                # to a task to create connections in neo
                created = str(datetime.now(pytz.utc))
                uuid = str(uuid1())
                table.put_item(
                    data={
                        "parent_object": parent_uuid,
                        "object_uuid": uuid,
                        "content": serializer.validated_data["content"],
                        "created": created,
                        "comment_owner": request.user.get_full_name(),
                        "comment_owner_email": request.user.email,
                        "last_edited_on": created,
                    }
                )
                return Response(serializer.validated_data,
                                status=status.HTTP_201_CREATED)

            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def upvote(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def downvote(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def close(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def protect(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)