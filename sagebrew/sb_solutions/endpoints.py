from datetime import datetime
from uuid import uuid1
import pytz
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
from sb_comments.utils import convert_dynamo_comments
from sb_comments.serializers import CommentSerializer

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
        serializer = self.serializer_class(single_object,
                                           context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, object_uuid=None):
        pass

    def partial_update(self, request, object_uuid=None):
        pass

    def destroy(self, request, object_uuid=None):
        pass

    @detail_route(methods=['get', 'post'], serializer_class=CommentSerializer)
    def comments(self, request, object_uuid=None):
        table = get_dynamo_table("comments")
        if isinstance(table, Exception) is True:
            logger.exception("SolutionGenericViewSet comment")
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