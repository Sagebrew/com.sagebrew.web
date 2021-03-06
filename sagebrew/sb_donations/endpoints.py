from rest_framework.response import Response
from rest_framework import status, viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from neomodel import db

from sb_missions.neo_models import Mission
from sb_quests.neo_models import Quest
from plebs.neo_models import Pleb

from .neo_models import Donation
from .serializers import DonationSerializer, SBDonationSerializer


class DonationViewSet(viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin):
    serializer_class = DonationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        query = 'MATCH (d:Donation {object_uuid: "%s"}) RETURN d' % \
                (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        res[0][0].pull()
        return Donation.inflate(res[0][0])

    def list(self, request, *args, **kwargs):
        """
        The reasoning behind having this list method here is so that in the
        future we can allow users to view all billed donations to the campaign
        since that should be public knowledge.
        """
        return Response({'detail': "Sorry, we currently do not allow for "
                                   "users to query all donations for every "
                                   "quest.",
                         'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, *args, **kwargs):
        if (request.user.username ==
                Donation.get_owner(self.kwargs[self.lookup_field])):
            return super(DonationViewSet, self).retrieve(request, *args,
                                                         **kwargs)
        return Response({"detail": "Sorry only the owner of a donation is "
                                   "allowed to see its detail page.",
                         "status_code": status.HTTP_403_FORBIDDEN},
                        status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if (request.user.username ==
                Donation.get_owner(self.kwargs[self.lookup_field])):
            if self.get_object().completed:
                return Response({"detail": "Sorry, you cannot delete a pledge "
                                           "which has already been "
                                           "processed.",
                                 "status_code": status.HTTP_403_FORBIDDEN},
                                status=status.HTTP_403_FORBIDDEN)
            return super(DonationViewSet, self).destroy(request, *args,
                                                        **kwargs)
        return Response({"detail": "Sorry only the owner of a donation is "
                                   "allowed to delete it.",
                         "status_code": status.HTTP_403_FORBIDDEN},
                        status=status.HTTP_403_FORBIDDEN)


class DonationListCreate(generics.ListCreateAPIView):
    """
    This endpoint will be utilized to allow accountants of a campaign to view
    the donations attached to the campaign. Also allows users to create
    donations on this endpoint. We set up some custom validation for the
    list method to only allow the owner or an accountant to view a list of
    donations attached to the campaign.
    """
    serializer_class = DonationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if "/v1/missions/" in self.request.path:
            query = 'MATCH (mission:Mission {object_uuid: "%s"})' \
                    '<-[:CONTRIBUTED_TO]-(donation:Donation) ' \
                    'RETURN donation' % self.kwargs[self.lookup_field]
        else:
            query = 'MATCH (quest:Quest {owner_username: "%s"})' \
                    '-[:EMBARKS_ON]->(mission:Mission)' \
                    '<-[:CONTRIBUTED_TO]-(donation:Donation) ' \
                    'RETURN donation' % self.kwargs[self.lookup_field]
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Donation.inflate(row[0]) for row in res]

    def perform_create(self, serializer):
        donor = Pleb.get(self.request.user.username)
        if "/v1/missions/" in self.request.path:
            mission = Mission.get(object_uuid=self.kwargs[self.lookup_field])
            quest = Mission.get_quest(
                object_uuid=self.kwargs[self.lookup_field])
        else:
            mission = None
            quest = Quest.get(owner_username=self.kwargs[self.lookup_field])
        serializer.save(mission=mission, donor=donor, quest=quest,
                        owner_username=donor.username)

    def list(self, request, *args, **kwargs):
        """
        Currently we limit this endpoint to only be accessible to
        owners/accountants of campaigns, this is because it displays all
        donations not just the completed ones. We will eventually want to add
        some functionality to this that will allow people who are not the
        owner/accountant of the campaign to view all completed donations.

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if "mission" in self.request.path:
            moderators = Mission.get(
                object_uuid=self.kwargs[self.lookup_field])
        else:
            moderators = Quest.get(
                owner_username=self.kwargs[self.lookup_field])
        if not (request.user.username in
                moderators.get_moderators(moderators.owner_username)):
            return Response({"status_code": status.HTTP_403_FORBIDDEN,
                             "detail": "You are not authorized to access "
                                       "this page."},
                            status=status.HTTP_403_FORBIDDEN)
        return super(DonationListCreate, self).list(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def sagebrew_donation(request):
    if not Pleb.get(request.user.username).is_verified:
        return Response(
            {
                "detail": "You cannot donate to us unless you are verified.",
                "status": status.HTTP_401_UNAUTHORIZED,
                "developer_message": "A user may only donate on Sagebrew "
                                     "if they are verified."},
            status=status.HTTP_401_UNAUTHORIZED)
    serializer = SBDonationSerializer(data=request.data,
                                      context={'request': request})
    if serializer.is_valid():
        serializer.save(token=request.data.get('token', None))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
