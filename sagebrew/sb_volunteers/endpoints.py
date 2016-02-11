import csv
from django.conf import settings
from django.http import HttpResponse
from django.core.files.temp import NamedTemporaryFile
from django.core.servers.basehttp import FileWrapper

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.exceptions import AuthenticationFailed

from neomodel import db

from api.permissions import IsOwnerOrModerator
from plebs.neo_models import Pleb
from sb_missions.neo_models import Mission

from .serializers import VolunteerSerializer
from .neo_models import Volunteer


class VolunteerViewSet(viewsets.ModelViewSet):
    serializer_class = VolunteerSerializer
    lookup_field = "volunteer_id"
    permission_classes = (IsAuthenticated,)

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

    def perform_destroy(self, instance):
        if self.request.user.username != instance.owner_username:
            raise AuthenticationFailed(
                "Sorry you're not authorized to do that")
        return super(VolunteerViewSet, self).perform_destroy(instance)

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

    @list_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def expanded_data(self, request, object_uuid=None):
        """
        Determines if the currently authenticated user has already volunteered
        for the related mission.
        :param object_uuid:
        :param request:
        :return:
        """
        query = 'MATCH (plebs:Pleb)-[:WANTS_TO]->(volunteer:Volunteer)' \
                '-[:ON_BEHALF_OF]->(mission:Mission {object_uuid:"%s"}) ' \
                'RETURN plebs, volunteer.activities AS activities' \
                % (object_uuid)
        res, _ = db.cypher_query(query)
        filtered_dict = {}
        for item in settings.VOLUNTEER_ACTIVITIES:
            filtered_dict[item[0]] = [
                {"first_name": row.plebs["first_name"],
                 "last_name": row.plebs["last_name"],
                 "email": row.plebs["email"],
                 "profile": reverse("profile_page",
                                    kwargs={"pleb_username":
                                            row.plebs["username"]})}
                for index, row in enumerate(res)
                if item[0] in res[index].activities]
        return Response(filtered_dict, status=status.HTTP_200_OK)

    @list_route(methods=['GET'], permission_classes=(IsAuthenticated,))
    def volunteer_export(self, request, object_uuid=None):
        mission = Mission.get(object_uuid)
        keys = []
        query = 'MATCH (plebs:Pleb)-[:WANTS_TO]->(volunteer:Volunteer)' \
                '-[:ON_BEHALF_OF]->(mission:Mission {object_uuid:"%s"}) ' \
                'RETURN plebs, volunteer.activities AS activities' \
                % (object_uuid)
        res, _ = db.cypher_query(query)
        try:
            filtered = [
                {"first_name": row.plebs["first_name"],
                 "last_name": row.plebs["last_name"],
                 "email": row.plebs["email"],
                 "activities": [
                     {item[0]: "x"} if item[0] in res[index].activities
                     else {item[0]: ""}
                     for item in settings.VOLUNTEER_ACTIVITIES]}
                for index, row in enumerate(res)]
            for item in filtered:
                for activity in item["activities"]:
                    item.update(activity)
                item.pop('activities', None)
            for key in filtered[0].keys():
                new_key = key.replace('_', ' ').title()
                for volunteer in filtered:
                    volunteer[new_key] = volunteer[key]
                    volunteer.pop(key, None)
                keys.append(new_key)
            fieldnames = ['First Name', 'Last Name', 'Email']
            newfile = NamedTemporaryFile(suffix='.csv', delete=False)
            newfile.name = "%s_mission_volunteers.csv" % mission.title
            dict_writer = csv.DictWriter(newfile, keys)
            dict_writer.writeheader()
            dict_writer.writerows(filtered)
            newfile.seek(0)
            wrapper = FileWrapper(newfile)
            httpresponse = HttpResponse(wrapper,
                                        content_type="text/csv")
            httpresponse['Content-Disposition'] = 'attachment; filename=%s' \
                                                  % newfile.name
            return httpresponse
        except IndexError:
            pass
        newfile = NamedTemporaryFile(suffix='.csv', delete=False)
        newfile.name = "%s_mission_volunteers.csv" % mission.title
        dict_writer = csv.DictWriter(newfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows([])
        newfile.seek(0)
        wrapper = FileWrapper(newfile)
        httpresponse = HttpResponse(wrapper,
                                    content_type="text/csv")
        httpresponse['Content-Disposition'] = 'attachment; filename=%s' \
                                              % newfile.name
        return httpresponse
