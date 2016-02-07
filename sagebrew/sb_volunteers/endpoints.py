from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db

from api.permissions import IsAdminOrReadOnly

from .serializers import VolunteerSerializer
from .neo_models import Volunteer


class VolunteerViewSet(viewsets.ModelViewSet):
    serializer_class = VolunteerSerializer
    lookup_field = "option"
    queryset = Volunteer.nodes.all()
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)

    def get_object(self):
        return Volunteer.nodes.get(name=self.kwargs[self.lookup_field])

    def get_queryset(self):
        query = "MATCH (vol:Volunteer) RETURN vol"
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Volunteer.inflate(row[0]) for row in res]

    @list_route(methods=['get'])
    def options(self, request, *args, **kwargs):
        query = "MATCH (a:Volunteer) RETURN a.option"
        res, _ = db.cypher_query(query)
        return Response([{"title": row[0].title(),
                          "option": row[0].replace(" ", "_")}
                         for row in res],
                        status=status.HTTP_200_OK)