import pytz
from datetime import datetime

from django.core.cache import cache

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)

from api.utils import spawn_task
from sb_docstore.tasks import spawn_user_updates
from plebs.neo_models import Pleb
from sb_search.tasks import update_search_object

from .serializers import VoteSerializer
from .utils import handle_vote


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
        object_uuid = self.kwargs[self.lookup_field]
        now = str(datetime.now(pytz.utc))
        vote_data = request.data
        serializer = self.get_serializer(data=vote_data,
                                         context={"request": request})
        if not Pleb.get(request.user.username).is_verified:
            return Response({
                "detail": "Sorry, you cannot vote unless you are verified!",
                "status": status.HTTP_401_UNAUTHORIZED,
                "developer_message": "A user can only vote on content "
                                     "if they are verified."
            }, status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            parent_object_uuid = self.kwargs[self.lookup_field]

            vote_status = int(serializer.validated_data['vote_type'])
            handle_vote(parent_object_uuid, vote_status,
                        request.user.username, now)
            async_result = cache.get("%s_%s_vote" % (request.user.username,
                                                     object_uuid))
            task_params = {
                "username": request.user.username,
                "object_uuid": object_uuid
            }
            if async_result is not None:
                # if there is already a task lined up,
                # revoke it and spawn a new one
                async_result.revoke()

            # spawn a task which will execute 30 seconds from now
            # potential improvement here is to have a way to detect if the
            new_task = spawn_task(spawn_user_updates,
                                  task_param=task_params,
                                  countdown=30)
            cache.set("%s_%s_vote" % (request.user.username, object_uuid),
                      new_task)
            search_result = cache.get("%s_vote_search_update" % object_uuid)
            if search_result is not None:
                search_result.revoke()
            task_param = {
                "object_uuid": object_uuid
            }
            spawned = spawn_task(task_func=update_search_object,
                                 task_param=task_param,
                                 countdown=10)
            cache.set("%s_vote_search_update" % object_uuid, spawned)
            return Response({"detail": "Successfully created or modified "
                                       "vote.",
                             "status": status.HTTP_200_OK,
                             "developer_message": None})
        else:
            return Response(serializer.errors, status=400)
