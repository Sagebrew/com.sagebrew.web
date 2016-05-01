from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from neomodel import db

from .serializers import AddressSerializer
from .neo_models import Address


class AddressViewSet(viewsets.ModelViewSet):
    """
    This ViewSet provides all of the addresses associated with the currently
    authenticated user. We don't want to enable users to view all addresses
    utilized on the site from an endpoint but this endpoint allows for users
    to see and modify their own as well as create new ones.

    Limitations:
    Currently we don't have a way to determine which address is the current
    address. We also don't have an interface to generate additional addresses
    so the address input during registration is the only address ever listed
    even though this should not be expected as in the future the list will
    grow as we all things like hometown, previous residences, and additional
    homes to be listed.

    Improvements:
    We may want to transition this to /v1/me/addresses/ and
    /v1/me/addresses/{id}/.
    """
    serializer_class = AddressSerializer
    lookup_field = 'object_uuid'
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address) RETURN b' % self.request.user.username
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Address.inflate(row[0]) for row in res]

    def get_object(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address {object_uuid: "%s"}) RETURN b' % (
                    self.request.user.username, self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return Address.inflate(res[0][0])
