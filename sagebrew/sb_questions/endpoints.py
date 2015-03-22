from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination

from neomodel import CypherException

from sagebrew import errors

from sb_docstore.utils import get_dynamo_table
from sb_solutions.utils import convert_dynamo_solutions

from .serializers import QuestionSerializerNeo
from .neo_models import SBQuestion


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
        single_object = self.get_object(object_uuid)
        if isinstance(single_object, Response):
            return single_object
        serializer = self.serializer_class(single_object,
                                           context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
            queryset = sorted(queryset, key=lambda k: k['object_vote_count'])
        # TODO probably want to replace with a serializer if we want to get
        # any urls returned. Or these could be stored off into dynamo based on
        # the initial pass on the serializer
        return Response(queryset, status=status.HTTP_200_OK)
