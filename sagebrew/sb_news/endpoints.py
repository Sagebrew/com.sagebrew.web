from neomodel import db
from rest_framework import viewsets

from api.permissions import (IsOwnerOrModeratorOrReadOnly, )

from .serializers import NewsArticleSerializer
from .neo_models import NewsArticle


class NewsArticleViewSet(viewsets.ModelViewSet):
    serializer_class = NewsArticleSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        query = 'MATCH (news:NewsArticle) RETURN news'
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [NewsArticle.inflate(row[0]) for row in res]

    def get_object(self):
        return NewsArticle.nodes.get(object_uuid=self.kwargs[self.lookup_field])
