from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import CypherException

from sagebrew import errors

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
            queryset = sorted(queryset, key=lambda k: k.get_vote_count(),
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
        html = self.request.query_params.get('html', 'false').lower()

        queryset = self.get_object(object_uuid)
        single_object = QuestionSerializerNeo(
            queryset, context={'request': request}).data
        single_object["last_edited_on"] = datetime.strptime(
            single_object['last_edited_on'][:len(
                single_object['last_edited_on']) - 6],
            '%Y-%m-%dT%H:%M:%S.%f')

        if html == "true":
            # This will be moved to JS Framework but don't need intermediate
            # step at the time being as this doesn't require pagination
            single_object["current_user_username"] = request.user.username
            return Response({"html": render_question_object(single_object),
                             "ids": [single_object["object_uuid"]],
                             "solution_count": single_object['solution_count']},
                            status=status.HTTP_200_OK)

        return Response(single_object, status=status.HTTP_200_OK)

    def update(self, request, object_uuid=None):
        pass

    def partial_update(self, request, object_uuid=None):
        pass

    def destroy(self, request, object_uuid=None):
        pass

    @detail_route(methods=['get'])
    def solution_count(self, request, object_uuid=None):
        # TODO count in dynamo is not being updated at this time.
        '''
        try:
            table = get_dynamo_table("public_solutions")
            queryset = table.query_2(parent_object__eq=object_uuid)
            solution_count = len(list(queryset))
            if solution_count == 0:
                raise AttributeError
            return Response({"solution_count": solution_count},
                            status=status.HTTP_200_OK)
        except(ItemNotFound, AttributeError, IOError):
        '''
        try:
            question = SBQuestion.nodes.get(object_uuid=object_uuid)
            return Response({"solution_count": len(question.solutions.all())},
                            status=status.HTTP_200_OK)
        except(CypherException, IOError) as e:
            logger.exception("CommentGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    def render(self, request):
        """
        This is a intermediate step on the way to utilizing a JS Framework to
        handle template rendering.
        """
        html_array = []
        id_array = []
        questions = self.list(request)

        for question in questions.data['results']:
            # This is a work around for django templates and our current
            # implementation of spacing for vote count in the template.
            question["vote_count"] = str(question["vote_count"])
            question['last_edited_on'] = datetime.strptime(
                question[
                    'last_edited_on'][:len(question['last_edited_on']) - 6],
                '%Y-%m-%dT%H:%M:%S.%f')
            html_array.append(render_to_string('question_summary.html',
                                               question))
            id_array.append(question["object_uuid"])
        questions.data['results'] = {"html": html_array, "ids": id_array}
        return Response(questions.data, status=status.HTTP_200_OK)