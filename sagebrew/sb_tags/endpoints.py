from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db

from api.permissions import IsAdminOrReadOnly

from .serializers import TagSerializer
from .neo_models import Tag


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    lookup_field = "name"
    queryset = Tag.nodes.all()
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)

    def get_object(self):
        return Tag.nodes.get(name=self.kwargs[self.lookup_field])

    def get_queryset(self):
        exclude_base = self.request.query_params.get('exclude_base', 'false')\
            .lower()
        query_mod = ""
        if exclude_base == 'true':
            query_mod = "WHERE t.base=false"
        query = "MATCH (t:Tag) %s RETURN t" % (query_mod)
        res, col = db.cypher_query(query)
        return [Tag.inflate(row[0]) for row in res]

    def create(self, request, *args, **kwargs):
        """
        Currently a profile is generated for a user when the base user is
        created. We currently don't support creating a profile through an
        endpoint due to the confirmation process and links that need to be
        made.
        :param request:
        :return:
        """
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def solutions(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @list_route(methods=['get'])
    def suggestion_engine(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            tag_list = []
            serializer = self.get_serializer(page, many=True)
            for tag in serializer.data:
                tag_list.append({'value': tag['name']})
            return self.get_paginated_response(tag_list)
        return Response({"detail": "Paginated data only, currently."},
                        status=status.HTTP_501_NOT_IMPLEMENTED)
