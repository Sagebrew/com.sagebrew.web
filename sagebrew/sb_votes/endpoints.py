import pytz
from datetime import datetime

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)

from sb_base.views import ObjectRetrieveUpdateDestroy

from .serializers import VoteSerializer
from .neo_models import Vote
from .utils import handle_vote


class ObjectVotesRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    # Currently this is not in use as people cannot access votes directly
    # we aren't storing off votes in Neo other than counts on objects
    serializer_class = VoteSerializer
    lookup_field = "object_uuid"
    lookup_url_kwarg = "comment_uuid"

    def get_object(self):
        return Vote.nodes.get(object_uuid=self.kwargs[self.lookup_url_kwarg])


class ObjectVotesListCreate(ListCreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        # Currently we don't do a queryset on votes. Instead we have counts
        # associated with the give objects the votes are on and update those
        # based on the values put into Dynamo
        return []

    def create(self, request, *args, **kwargs):
        now = unicode(datetime.now(pytz.utc))
        vote_data = request.data
        serializer = self.get_serializer(data=vote_data,
                                         context={"request": request})
        if serializer.is_valid():
            parent_object_uuid = self.kwargs[self.lookup_field]

            vote_status = int(serializer.validated_data['vote_type'])
            res = handle_vote(parent_object_uuid, vote_status,
                              request.user.username, now)
            if res:
                return Response({"detail": "Successfully created or modified "
                                           "vote.",
                                 "status": status.HTTP_200_OK,
                                 "developer_message": None})
            return Response({"detail": ""})
        else:
            return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def vote_list(request):
    # TODO instead want to make a list of all the user's existing votes that
    # has a IsSelf permission set. This will enable us to eventually allow users
    # to get to all the items they've voted on and do an analysis of the info
    response = {"status": status.HTTP_501_NOT_IMPLEMENTED,
                "detail": "We do not allow users to query all the votes on"
                          "the site.",
                "developer_message":
                    "Please access votes per user and total counts via their "
                    "corresponding content object."
                }
    return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)
