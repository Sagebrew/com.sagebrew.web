from django.conf import settings

from neomodel import db
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

from api.utils import (calc_stripe_application_fee, humanize_dict_keys,
                       generate_csv_html_file_response)
from sb_base.utils import NeoQuerySet
from sb_donations.serializers import DonationExportSerializer
from api.permissions import (IsOwnerOrModeratorOrReadOnly, IsOwnerOrModerator)
from plebs.neo_models import Pleb
from plebs.serializers import PlebSerializerNeo
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer
from sb_council.serializers import MissionReviewSerializer

from .serializers import MissionSerializer
from .neo_models import Mission


class MissionViewSet(viewsets.ModelViewSet):
    serializer_class = MissionSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsOwnerOrModeratorOrReadOnly,)

    def get_queryset(self):
        if self.request.query_params.get('affects', "") == "me":
            query = '(pleb:Pleb {username: "%s"})-[:LIVES_AT]->' \
                    '(address:Address)-[:ENCOMPASSED_BY*..]->' \
                    '(location:Location)<-[:WITHIN]-' \
                    '(res:Mission {active: true})<-[:EMBARKS_ON]-' \
                    '(quest:Quest {active: true})' % self.request.user.username
        elif self.request.query_params.get('affects', "") == "friends":
            query = '(pleb:Pleb {username: "%s"})-[:FOLLOWING]' \
                    '->(friends:Pleb)-[:LIVES_AT]->' \
                    '(address:Address)-[:ENCOMPASSED_BY*..]->' \
                    '(location:Location)<-[:WITHIN]-' \
                    '(res:Mission {active: true})<-[:EMBARKS_ON]-' \
                    '(quest:Quest {active: true})' % self.request.user.username
        elif self.request.query_params.get(
                'submitted_for_review', "") == "true":
            active = self.request.query_params.get('active', '')
            if active == 'true' or active == 'false':
                query = '(res:Mission {submitted_for_review:true, ' \
                        'active:%s})' % (active)
        else:
            query = '(res:Mission {active: true})<-[:EMBARKS_ON]-' \
                    '(quest:Quest {active: true})'
        return NeoQuerySet(
            Mission, query=query, distinct=True, descending=True) \
            .filter('WHERE NOT ((res)-[:FOCUSED_ON]->'
                    '(:Position {verified:false}))') \
            .order_by('ORDER BY res.created')

    def get_object(self):
        return Mission.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        query = 'MATCH (a:Pleb {username: "%s"})-[IS_WAGING]->(b:Quest) ' \
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
        :param object_uuid:
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
        defined_keys = ["First Name", "Last Name", "Email", "City", "State"] + \
                       [act[1] for act in settings.VOLUNTEER_ACTIVITIES]
        query = 'MATCH (plebs:Pleb)-[:WANTS_TO]->(volunteer:Volunteer)' \
                '-[:ON_BEHALF_OF]->(mission:Mission {object_uuid:"%s"}) ' \
                'WITH plebs, volunteer ' \
                'OPTIONAL MATCH (plebs)-[:LIVES_AT]->(address:Address) ' \
                'RETURN plebs, volunteer.activities AS activities, address' \
                % object_uuid
        res, _ = db.cypher_query(query)
        try:
            filtered = [
                {"first_name": row.plebs["first_name"],
                 "last_name": row.plebs["last_name"],
                 "email": row.plebs["email"],
                 "city": row.address['city']
                    if row.address is not None else "N/A",
                 "state": row.address['state']
                    if row.address is not None else "N/A",
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

    @detail_route(methods=['POST'], permission_classes=(IsAuthenticated,
                                                        IsOwnerOrModerator,))
    def endorse(self, request, object_uuid=None):
        endorse_as = request.data.get('endorse_as')
        if not endorse_as:
            return Response({"detail": "You must specify if you will be "
                                       "endorsing as a User or as a Quest",
                             "status": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)
        Mission.endorse(object_uuid, request.user.username, endorse_as)
        return Response({"detail": "Successfully Endorsed Mission",
                         "status_code": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['POST'], permission_classes=(IsAuthenticated,
                                                        IsOwnerOrModerator,))
    def unendorse(self, request, object_uuid=None):
        endorse_as = request.data.get('endorse_as')
        Mission.unendorse(object_uuid, request.user.username, endorse_as)
        return Response({"detail": "Successfully Endorsed Mission",
                         "status_code": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def endorsements(self, request, object_uuid=None):
        serialized = []
        endorsements = Mission.get_endorsements(object_uuid)
        page = self.paginate_queryset(endorsements)
        for node in page:
            if "Pleb" in node.labels:
                serialized.append(PlebSerializerNeo(Pleb.inflate(node.e)).data)
            if "Quest" in node.labels:
                serialized.append(QuestSerializer(Quest.inflate(node.e)).data)
        return self.get_paginated_response(serialized)

    @detail_route(methods=['POST'], permission_classes=(IsAuthenticated,
                                                        IsOwnerOrModerator,))
    def reset_epic(self, request, object_uuid=None):
        Mission.reset_epic(object_uuid)
        return Response({"detail": "Successfully Reset Epic",
                         "status_code": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['PATCH'], permission_classes=(IsAuthenticated,),
                  serializer_class=MissionReviewSerializer)
    def review(self, request, object_uuid=None):
        if request.user.username == 'tyler_wiersing' \
                or request.user.username == 'devon_bleibtrey':
            query = 'MATCH (m:Mission {object_uuid:"%s"}) RETURN m' \
                    % object_uuid
            res, _ = db.cypher_query(query)
            serializer = self.get_serializer(Mission.inflate(res.one),
                                             data=request.data, partial=True)
            if serializer.is_valid():
                self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
