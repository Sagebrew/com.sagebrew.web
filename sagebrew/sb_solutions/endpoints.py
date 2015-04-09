from datetime import datetime

from logging import getLogger

from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import (RetrieveUpdateDestroyAPIView,
                                     ListCreateAPIView)

from neomodel import CypherException

from sagebrew import errors
from sb_questions.neo_models import SBQuestion

from .serializers import SolutionSerializerNeo
from .neo_models import SBSolution


logger = getLogger('loggly_logs')


class SolutionViewSet(viewsets.GenericViewSet):
    """

    """
    serializer_class = SolutionSerializerNeo
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        try:
            queryset = SBSolution.nodes.all()
        except(CypherException, IOError):
            logger.exception("SolutionGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        sort_by = self.request.query_params.get('ordering', None)
        if sort_by == "-created":
            queryset = sorted(queryset, key=lambda k: k.created, reverse=True)
        elif sort_by == "last_edited_on":
            queryset = sorted(queryset, key=lambda k: k.last_edited_on)
        else:
            queryset = sorted(queryset, key=lambda k: k.get_vote_count())

        return queryset

    def get_object(self, object_uuid=None):
        try:
            queryset = SBSolution.nodes.get(object_uuid=object_uuid)
        except(CypherException, IOError):
            logger.exception("SolutionViewSet queryset")
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
        pass

    def retrieve(self, request, object_uuid=None):
        single_object = self.get_object(object_uuid)
        if isinstance(single_object, Response):
            return single_object
        serializer = self.get_serializer(single_object,
                                         context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, object_uuid=None):
        pass

    def partial_update(self, request, object_uuid=None):
        pass

    def destroy(self, request, object_uuid=None):
        pass


class ObjectSolutionsRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    serializer_class = SolutionSerializerNeo
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"
    lookup_url_kwarg = "solution_uuid"

    def get_queryset(self):
        try:
            queryset = SBSolution.nodes.all()
        except(CypherException, IOError):
            logger.exception("CommentGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return sorted(queryset, key=lambda k: k.created, reverse=True)

    def get_object(self):
        try:
            queryset = SBSolution.nodes.get(
                object_uuid=self.kwargs[self.lookup_url_kwarg])
        except(CypherException, IOError):
            logger.exception("CommentRetrieveUpdateDestroy get_object")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return queryset


class ObjectSolutionsListCreate(ListCreateAPIView):
    serializer_class = SolutionSerializerNeo
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        # TODO Commented out because we need to figure out how to do pagination
        # with the doc store. Right now DRF doesn't work out of the box with
        # a dictionary type. So we could potentially populate a node object
        # with the dict and not save it but use it to move the data around
        # but haven't had time to test this out.
        '''
        try:
            table = get_dynamo_table("public_solutions")
            if isinstance(table, Exception) is True:
                logger.exception("QuestionsViewSet solutions")
                return Response(errors.DYNAMO_TABLE_EXCEPTION,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            queryset = table.query_2(
                parent_object__eq=self.kwargs[self.lookup_field])
            queryset = convert_dynamo_solutions(queryset, self.request)
            if len(queryset) == 0:
                raise ItemNotFound
        except(ItemNotFound, AttributeError, IOError):
        '''
        try:
            question = SBQuestion.nodes.get(
                object_uuid=self.kwargs[self.lookup_field])
            queryset = question.solutions.all()
        except(CypherException, IOError) as e:
            logger.exception("CommentGenericViewSet queryset")
            return Response(errors.CYPHER_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ordering = self.request.query_params.get('ordering', None)
        if ordering == "-created":
            queryset = sorted(queryset, key=lambda k: k.created,
                              reverse=True)
        elif ordering == "-last_edited_on":
            queryset = sorted(queryset, key=lambda k: k.last_edited_on,
                              reverse=True)
        else:
            queryset = sorted(queryset, key=lambda k: k.get_vote_count(),
                              reverse=True)
        return queryset

    def list(self, request, *args, **kwargs):
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

    def create(self, request, *args, **kwargs):
        pass


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def solution_renderer(request, object_uuid=None):
    '''
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    '''
    html_array = []
    id_array = []
    args = []
    kwargs = {"object_uuid": object_uuid}
    solutions = ObjectSolutionsListCreate.as_view()(request, *args, **kwargs)
    for solution in solutions.data['results']:
        # This is a work around for django templates and our current
        # implementation of spacing for vote count in the template.
        solution["vote_count"] = str(solution["vote_count"])
        solution['last_edited_on'] = datetime.strptime(
            solution['last_edited_on'][:len(solution['last_edited_on']) - 6],
            '%Y-%m-%dT%H:%M:%S.%f')
        solution["current_user_username"] = request.user.username
        html_array.append(render_to_string('solution.html',  solution))
        id_array.append(solution["object_uuid"])
    solutions.data['results'] = {"html": html_array, "ids": id_array}

    return Response(solutions.data, status=status.HTTP_200_OK)