from logging import getLogger

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination

from neomodel import CypherException

from sagebrew import errors

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

        sort_by = self.request.query_params.get('sort_by', None)
        if sort_by == "created":
            queryset = sorted(queryset, key=lambda k: k.created)
        elif sort_by == "edited":
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
