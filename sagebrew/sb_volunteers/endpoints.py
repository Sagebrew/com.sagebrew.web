from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route

from neomodel import db

from api.permissions import IsAuthorizedAndVerified
from plebs.neo_models import Pleb
from sb_missions.neo_models import Mission

from .serializers import VolunteerSerializer
from .neo_models import Volunteer


class VolunteerViewSet(viewsets.ModelViewSet):
    serializer_class = VolunteerSerializer
    lookup_field = "volunteer_id"
    permission_classes = (IsAuthorizedAndVerified,)

    def get_queryset(self):
        query = 'MATCH (mission:Mission {object_uuid: "%s"})' \
                '<-[:ON_BEHALF_OF]-(volunteer:Volunteer) ' \
                'RETURN volunteer' % self.kwargs["object_uuid"]
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Volunteer.inflate(row[0]) for row in res]

    def get_object(self):
        query = 'MATCH (volunteer:Volunteer {object_uuid: "%s"}) ' \
                'RETURN volunteer' % self.kwargs[self.lookup_field]
        res, _ = db.cypher_query(query)
        return Volunteer.inflate(res.one)

    def perform_create(self, serializer):
        volunteer = Pleb.get(self.request.user.username)
        mission = Mission.get(object_uuid=self.kwargs["object_uuid"])
        serializer.save(mission=mission, volunteer=volunteer,
                        owner_username=volunteer.username)

    def list(self, request, *args, **kwargs):
        moderators = Mission.get(object_uuid=self.kwargs["object_uuid"])
        if not (request.user.username in
                moderators.get_moderators(moderators.owner_username) and
                request.method == "GET"):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        return super(VolunteerViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def me(self, request, object_uuid=None):
        """
        Determines if the currently authenticated user has already volunteered
        for the related mission.
        :param object_uuid:
        :param request:
        :return:
        """
        query = 'MATCH (pleb:Pleb {username: "%s"})-[:WANTS_TO]->' \
                '(volunteer:Volunteer)-[:ON_BEHALF_OF]->' \
                '(mission:Mission {object_uuid: "%s"}) ' \
                'RETURN volunteer' % (request.user.username, object_uuid)
        res, _ = db.cypher_query(query)
        if res.one:
            volunteered = VolunteerSerializer(Volunteer.inflate(res.one),
                                              context={"request": request}).data
        else:
            volunteered = None

        return Response({"volunteered": volunteered,
                         "status_code": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)
