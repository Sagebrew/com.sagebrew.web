from uuid import uuid1
from datetime import datetime
import pytz
from logging import getLogger
from boto.dynamodb2.exceptions import ItemNotFound

from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.exceptions import NotFound

from neomodel import CypherException

from sagebrew import errors

from api.utils import request_to_api
from sb_docstore.utils import (get_dynamo_table, convert_dynamo_content,
                               get_vote)
from sb_solutions.utils import convert_dynamo_solutions, render_solutions
from sb_comments.serializers import CommentSerializer
from sb_comments.utils import convert_dynamo_comments
from sb_votes.utils import determine_vote_type

from .serializers import QuestionSerializerNeo
from .neo_models import SBQuestion
from .utils import render_question_object


logger = getLogger('loggly_logs')


class QuestionViewSet(viewsets.GenericViewSet):
    serializer_class = QuestionSerializerNeo
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)
    # Tried a filtering class but it requires a order_by method to be defined
    # on the given queryset. Since django provides an actual QuerySet rather
    # than a plain list this works with the ORM but would require additional
    # implementation in neomodel. May be something we want to look into to
    # simplify the sorting logic in our queryset methods

    def get_queryset(self):
        try:
            queryset = SBQuestion.nodes.all()
        except(CypherException, IOError):
            logger.exception("QuestionGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        sort_by = self.request.query_params.get('ordering', None)
        if sort_by == "created":
            queryset = sorted(queryset, key=lambda k: k.created)
        elif sort_by == "-created":
            queryset = sorted(queryset, key=lambda k: k.created, reverse=True)
        elif sort_by == "last_edited_on":
            queryset = sorted(queryset, key=lambda k: k.last_edited_on,
                              reverse=True)
        else:
            queryset = sorted(queryset, key=lambda k: k.vote_count,
                              reverse=True)

        return queryset

    def get_object(self, object_uuid=None):
        try:
            queryset = SBQuestion.nodes.get(object_uuid=object_uuid)
        except(CypherException, IOError):
            logger.exception("QuestionViewSet get_object")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        # As a note this if is the only difference between this list
        # implementation and the default ListModelMixin. Not sure if we need
        # to redefine everything...
        if isinstance(queryset, Response):
            return queryset
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True,
                                             context={"request": request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset, context={"request": request}, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            instance = self.get_serializer(instance)
            return Response(instance.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, object_uuid=None):
        table = get_dynamo_table("public_questions")
        if isinstance(table, Exception) is True:
            logger.exception("QuestionsViewSet get_object")
            return Response(errors.DYNAMO_TABLE_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        html = self.request.query_params.get('html', 'false').lower()
        expand = self.request.query_params.get('expand', "false").lower()
        if html == "true":
            expand = "true"
        try:
            queryset = table.get_item(object_uuid=object_uuid)
            try:
                if expand == "false":
                    single_object = convert_dynamo_content(queryset)
                else:
                    single_object = convert_dynamo_content(
                        queryset, self.request, "question-comments")
            except IndexError as e:
                raise NotFound
            single_object["profile"] = reverse(
                'profile_page', kwargs={
                    'pleb_username': single_object["owner"]
                }, request=request)
            user_url = reverse('user-detail', kwargs={
                'username': single_object["owner"]}, request=request)
            single_object["is_closed"] = int(single_object["is_closed"])
            if expand == "true":
                user_url = "%s%s" % (user_url, "?expand=True")
                response = request_to_api(user_url,
                                          request.user.username,
                                          req_method="GET")
                response_json = response.json()
                single_object["profile"] = response_json.pop("profile", None)
                single_object["owner_object"] = response_json
            else:
                single_object["owner_object"] = user_url
                single_object["profile"] = reverse('profile-detail', kwargs={
                    'username': single_object["owner"]}, request=request)
                single_object["comments"] = reverse(
                    "question-comments", kwargs={'object_uuid': object_uuid},
                    request=request)
        except ItemNotFound:
            queryset = self.get_object(object_uuid)
            single_object = QuestionSerializerNeo(
                queryset, context={'request': request}).data
            single_object["last_edited_on"] = datetime.strptime(
                    single_object[
                        'last_edited_on'][:len(
                        single_object['last_edited_on']) - 6],
                    '%Y-%m-%dT%H:%M:%S.%f')
            # TODO if get here should spawn task to repopulate question

        if html == "true":
            # This will be moved to JS Framework but don't need intermediate
            # step at the time being as this doesn't require pagination
            single_object['vote_type'] = determine_vote_type(
                single_object['object_uuid'], request.user.username)
            single_object["current_user_username"] = request.user.username
            return Response({"html": render_question_object(single_object),
                             "ids": [single_object["object_uuid"]]},
                            status=status.HTTP_200_OK)

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
        sort_by = self.request.query_params.get('sort_by', None)
        if sort_by == "created":
            queryset = sorted(queryset, key=lambda k: k['created'],
                              reverse=True)
        elif sort_by == "edited":
            queryset = sorted(queryset, key=lambda k: k['last_edited_on'],
                              reverse=True)
        else:
            queryset = sorted(queryset, key=lambda k: k['vote_count'],
                              reverse=True)
        # TODO probably want to replace with a serializer if we want to get
        # any urls returned. Or these could be stored off into dynamo based on
        # the initial pass on the serializer
        html = self.request.query_params.get('html', 'false').lower()

        if html == "true":
            id_array = []
            for item in queryset:
                id_array.append(item["object_uuid"])
            solution_dict = {
                "solution_count": len(queryset),
                "solutions": queryset,
                "email": request.user.email,
                "current_user_username": request.user.username,
            }
            return Response({"html": render_solutions(solution_dict),
                             "ids":id_array},
                            status=status.HTTP_200_OK)
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
            converted = convert_dynamo_comments(queryset)
            for comment in converted:
                user_url = "%s?expand=true" % reverse(
                    'user-detail', kwargs={'username': comment["owner"]},
                    request=request)
                response = request_to_api(user_url, request.user.username,
                                          req_method="GET")
                comment['owner'] = response.json()
                vote_type = get_vote(comment['object_uuid'],
                                     request.user.username)
                if vote_type is not None:
                    if vote_type['status'] == 2:
                        vote_type = None
                    else:
                        vote_type = str(bool(vote_type['status'])).lower()
                comment['vote_type'] = vote_type
            return Response(converted, status=status.HTTP_200_OK)
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

    @list_route(methods=['get'])
    def renderer(self, request):
        '''
        This is a intermediate step on the way to utilizing a JS Framework to
        handle template rendering.
        '''
        html_array = []
        id_array = []
        questions = self.list(request)

        for question in questions.data['results']:
            question['vote_type'] = determine_vote_type(
                question['object_uuid'], request.user.username)
            question['last_edited_on'] = datetime.strptime(
                question[
                    'last_edited_on'][:len(question['last_edited_on']) - 6],
                '%Y-%m-%dT%H:%M:%S.%f')
            html_array.append(render_to_string('question_summary.html',
                                               question))
            id_array.append(question["object_uuid"])
        questions.data['results'] = {"html": html_array, "ids": id_array}
        return Response(questions.data, status=status.HTTP_200_OK)