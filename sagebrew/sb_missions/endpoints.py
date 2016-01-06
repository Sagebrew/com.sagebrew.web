import csv
from django.conf import settings
from django.http import HttpResponse
from django.core.files.temp import NamedTemporaryFile
from django.core.servers.basehttp import FileWrapper

from neomodel import db
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

from sb_donations.neo_models import Donation
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

    def create(self, request, *args, **kwargs):
        query = 'MATCH (a:Pleb {username: "%s"})-[IS_WAGING]->(b:Quest)' \
                'RETURN b' % request.user.username
        res, _ = db.cypher_query(query)
        if res.one is None:
            self.permission_denied(request)
        return super(MissionViewSet, self).create(request, *args, **kwargs)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrModerator,))
    def pledged_votes_per_day(self, request, object_uuid=None):
        queryset = self.get_object().pledged_votes_per_day()
        return Response(queryset, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,
                                                       IsOwnerOrModerator,))
    def donation_data(self, request, object_uuid=None):
        """
        This endpoint allows for the owner or accountants to get a .csv file
        containing all of the data for donations given to the campaign.

        :param request:
        :param owner_username:
        :return:
        """
        self.check_object_permissions(request, object_uuid)
        donation_info = [DonationExportSerializer(
            Donation.inflate(donation)).data for donation in
            Mission.get_donations(object_uuid)]
        from logging import getLogger
        logger = getLogger('loggly_logs')
        logger.info(donation_info)
        mission = self.get_object()
        quest = Mission.get_quest(mission.object_uuid)
        # this loop merges the 'owned_by' and 'address' dictionaries into
        # the top level dictionary, allows for simple writing to csv
        try:
            for donation in donation_info:
                donation.update(donation.pop('owned_by', {}))
                donation.update(donation.pop('address', {}))
                application_fee = donation['amount'] * (
                    quest.application_fee +
                    settings.STRIPE_TRANSACTION_PERCENT) + .3
                donation['amount'] -= application_fee
            keys = []
            for key in donation_info[0].keys():
                new_key = key.replace('_', ' ').title()
                for donation in donation_info:
                    donation[new_key] = donation[key]
                    donation.pop(key, None)
                keys.append(new_key)
            # use of named temporary file here is to handle deletion of file
            # after we return the file, after the new file object is evicted
            # it gets deleted
            # http://stackoverflow.com/questions/3582414/removing-tmp-file-
            # after-return-httpresponse-in-django
            newfile = NamedTemporaryFile(suffix='.csv', delete=False)
            newfile.name = "%s_mission_donations.csv" % mission.title
            dict_writer = csv.DictWriter(newfile, keys)
            dict_writer.writeheader()
            dict_writer.writerows(donation_info)
            # the HttpResponse use here allows us to do an automatic download
            # upon hitting the button
            newfile.seek(0)
            wrapper = FileWrapper(newfile)
            httpresponse = HttpResponse(wrapper,
                                        content_type="text/csv")
            httpresponse['Content-Disposition'] = 'attachment; filename=%s' \
                                                  % newfile.name
            return httpresponse
        except IndexError:
            return Response({'detail': 'Unable to find any donation data',
                             'status_code':
                                 status.HTTP_404_NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)
