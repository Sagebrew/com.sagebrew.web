from uuid import uuid1

from django.utils.text import slugify

from rest_framework.reverse import reverse
from rest_framework.permissions import (IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

from neomodel import db

from sb_base.views import ObjectRetrieveUpdateDestroy
from sb_quests.neo_models import Quest
from sb_missions.neo_models import Mission

from .serializers import UpdateSerializer
from .neo_models import Update


class UpdateListCreate(generics.ListCreateAPIView):
    serializer_class = UpdateSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if self.request.query_params.get('about_type') == 'mission' \
                or 'mission' in self.request.path:
            query = 'MATCH (updates:Update)-[:ABOUT]->' \
                    '(mission:Mission {object_uuid: "%s"}) ' \
                    'RETURN updates ORDER BY updates.created ' \
                    'DESC' % self.kwargs[self.lookup_field]
        else:
            query = 'MATCH (quest:Quest {owner_username:"%s"})-' \
                    '[:CREATED_AN]->(u:Update) return u ' \
                    'ORDER BY u.created DESC' % \
                    (self.kwargs[self.lookup_field])
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Update.inflate(row[0]) for row in res]

    def get_object(self):
        return Update.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        object_uuid = str(uuid1())
        if self.request.data.get('about_type') == "mission" \
                or 'mission' in self.request.path:
            about = Mission.get(self.kwargs[self.lookup_field])
            quest = Quest.get(about.owner_username)
            url = reverse('mission_updates', kwargs={
                'object_uuid': self.kwargs[self.lookup_field],
                'slug': slugify(about.get_mission_title())
            }, request=self.request)
        else:
            # If all else fails assume this update is about the Quest itself
            quest = Quest.get(self.kwargs[self.lookup_field])
            # TODO update quest url generation when we have an updates for
            # quest
            url = None
            about = quest
        serializer.save(
            quest=quest, about=about, url=url, object_uuid=object_uuid,
            href=reverse('update-detail', kwargs={'object_uuid': object_uuid},
                         request=self.request)
        )

    def create(self, request, *args, **kwargs):
        if self.request.data.get('about_type') == "mission":
            mission = Mission.get(self.kwargs[self.lookup_field])
            quest = Quest.get(mission.owner_username)
            if quest is None:
                return Response({
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "detail": "Sorry we couldn't find the Quest you were "
                              "attempting to create an update for."
                }, status=status.HTTP_404_NOT_FOUND)
            if quest.owner_username == request.user.username:
                return super(UpdateListCreate, self).create(request, *args,
                                                            **kwargs)
        if request.user.username not in \
                Quest.get_quest_helpers(self.kwargs[self.lookup_field]):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        return super(UpdateListCreate, self).create(request, *args, **kwargs)


class UpdateRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = UpdateSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self):
        return Update.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Sorry we do not allow deletion of updates.",
             "status_code": status.HTTP_405_METHOD_NOT_ALLOWED},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)
