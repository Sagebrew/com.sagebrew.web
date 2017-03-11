from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from neomodel import db

from sagebrew.sb_gifts.neo_models import Giftlist
from sagebrew.sb_gifts.serializers import GiftlistSerializer


class GiftListViewSet(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = GiftlistSerializer

    def get_object(self):
        query = 'MATCH (mission:Mission {object_uuid:"%s"})<-[:LIST_FOR]-' \
                '(g:Giftlist) RETURN g' % self.kwargs[self.lookup_field]
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return Giftlist.inflate(res.one)
