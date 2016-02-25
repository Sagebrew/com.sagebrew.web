from django.conf import settings

from neomodel import db
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

from api.utils import (calc_stripe_application_fee, humanize_dict_keys,
                       generate_csv_html_file_response)
from sb_donations.serializers import DonationExportSerializer
from api.permissions import (IsOwnerOrModeratorOrReadOnly, IsOwnerOrModerator)

from .serializers import MissionSerializer
from .neo_models import Mission


class MissionViewSet(viewsets.ModelViewSet):
    serializer_class = MissionSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        if self.request.query_params.get('affects', "") == "me":
            query = 'MATCH (pleb:Pleb {username: "%s"})-[:LIVES_AT]->' \
                    '(address:Address)-[:ENCOMPASSED_BY*..]->' \
                    '(location:Location)<-[:WITHIN]-' \
                    '(mission:Mission {active: true})<-[:EMBARKS_ON]-' \
                    '(quest:Quest {active: true}) ' \
                    'RETURN DISTINCT mission' % self.request.user.username
        elif self.request.query_params.get('affects', "") == "friends":
            query = 'MATCH (pleb:Pleb {username: "%s"})-[:FRIENDS_WITH]' \
                    '->(friends:Pleb)-[:LIVES_AT]->' \
                    '(address:Address)-[:ENCOMPASSED_BY*..]->' \
                    '(location:Location)<-[:WITHIN]-' \
                    '(mission:Mission {active: true})<-[:EMBARKS_ON]-' \
                    '(quest:Quest {active: true}) ' \
                    'RETURN DISTINCT mission' % self.request.user.username
        else:
            query = 'MATCH (a:Mission {active: true})<-[:EMBARKS_ON]-' \
                    '(quest:Quest {active: true}) RETURN a'
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Mission.inflate(row[0]) for row in res]

    def get_object(self):
        return Mission.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        serializer.save(verified=self.request.data.get('verified'))

    def create(self, request, *args, **kwargs):
        query = 'MATCH (a:Pleb {username: "%s"})-[IS_WAGING]->(b:Quest)' \
                'RETURN b' % request.user.username
        res, _ = db.cypher_query(query)
        if res.one is None:
            self.permission_denied(request)
        return super(MissionViewSet, self).create(request, *args, **kwargs)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrModerator,))
    def donation_data(self, request, object_uuid=None):
        """
        This endpoint allows for the owner or accountants to get a .csv file
        containing all of the data for donations given to the mission.

        :param request:
        :param owner_username:
        :return:
        """
        mission = self.get_object()
        self.check_object_permissions(request, mission.owner_username)
        keys = []
        donation_info = DonationExportSerializer(
            Mission.get_donations(object_uuid=object_uuid), many=True).data

        quest = Mission.get_quest(mission.object_uuid)
        # this loop merges the 'owned_by' and 'address' dictionaries into
        # the top level dictionary, allows for simple writing to csv
        try:
            for donation in donation_info:
                donation.update(donation.pop('owned_by', {}))
                donation.update(donation.pop('address', {}))
                application_fee = calc_stripe_application_fee(
                    donation['amount'], quest.application_fee)
                donation['amount'] = '{:,.2f}'.format(
                    float(donation['amount'] - application_fee) / 100)
            humanized, new_keys = \
                humanize_dict_keys(donation_info, donation_info[0].keys())
            return generate_csv_html_file_response(
                "%s_mission_donations.csv" % mission.title, humanized, new_keys)
        except IndexError:
            pass
        return generate_csv_html_file_response(
            "%s_mission_donations.csv" % mission.title, [], keys)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrModerator,))
    def volunteer_data(self, request, object_uuid=None):
        mission = Mission.get(object_uuid)
        self.check_object_permissions(request, mission.owner_username)
        defined_keys = ["First Name", "Last Name", "Email", "City", "State",
                        "Get Out The Vote", "Assist With An Event",
                        "Leaflet Voters", "Write Letters To The Editor",
                        "Work In A Campaign Office",
                        "Table At Events", "Call Voters", "Data Entry",
                        "Host A Meeting", "Host A Fundraiser",
                        "Host A House Party", "Attend A House Party"]
        query = 'MATCH (plebs:Pleb)-[:WANTS_TO]->(volunteer:Volunteer)' \
                '-[:ON_BEHALF_OF]->(mission:Mission {object_uuid:"%s"}) ' \
                'WITH plebs, volunteer ' \
                'OPTIONAL MATCH (plebs)-[:LIVES_AT]->(address:Address) ' \
                'RETURN plebs, volunteer.activities AS activities, address' \
                % (object_uuid)
        res, _ = db.cypher_query(query)
        try:
            filtered = [
                {"first_name": row.plebs["first_name"],
                 "last_name": row.plebs["last_name"],
                 "email": row.plebs["email"],
                 "city": row.address["city"],
                 "state": row.address["state"],
                 "activities": [
                     {item[0]: "x"} if item[0] in res[index].activities
                     else {item[0]: ""}
                     for item in settings.VOLUNTEER_ACTIVITIES]}
                for index, row in enumerate(res)]
            for item in filtered:
                [item.update(activity) for activity in item["activities"]]
                item.pop('activities', None)
            humanized, _ = \
                humanize_dict_keys(filtered, filtered[0].keys())
            return generate_csv_html_file_response(
                "%s_mission_volunteers.csv" % mission.title, humanized,
                defined_keys)
        except IndexError:
            pass
        return generate_csv_html_file_response(
            "%s_mission_volunteers.csv" % mission.title, [], defined_keys)
