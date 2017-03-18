from rest_framework import viewsets

from sagebrew.api.permissions import (IsOwnerOrModeratorOrReadOnly, )
from sagebrew.sb_base.utils import NeoQuerySet

from .serializers import NewsArticleSerializer
from .neo_models import NewsArticle


class NewsArticleViewSet(viewsets.ModelViewSet):
    serializer_class = NewsArticleSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        return NeoQuerySet(NewsArticle)

    def get_object(self):
        return NewsArticle.nodes.get(object_uuid=self.kwargs[self.lookup_field])
