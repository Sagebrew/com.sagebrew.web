from django.core.cache import cache

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)

from neomodel import db

from sb_base.neo_models import SBContent
from sb_base.views import ObjectRetrieveUpdateDestroy
from plebs.neo_models import Pleb

from .neo_models import Flag
from .serializers import FlagSerializer


class ObjectFlagsRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = FlagSerializer
    lookup_field = "object_uuid"
    lookup_url_kwarg = "flag_uuid"

    def get_object(self):
        return Flag.nodes.get(
            object_uuid=self.kwargs[self.lookup_url_kwarg])


class ObjectFlagsListCreate(ListCreateAPIView):
    serializer_class = FlagSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (a:SBContent {object_uuid:'%s'})-[:HAS_FLAG]->" \
                "(b:Flag) WHERE a.to_be_deleted=false" \
                " RETURN b ORDER BY b.created " \
                "DESC" % (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Flag.inflate(row[0]) for row in res]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request})
        if serializer.is_valid():
            pleb = Pleb.get(request.user.username)
            parent_object = cache.get(self.kwargs[self.lookup_field])
            if parent_object is None:
                parent_object = SBContent.nodes.get(
                    object_uuid=self.kwargs[self.lookup_field])
                # Don't set it here as only questions will be
                # retrievable/settable

            serializer.save(owner=pleb, parent_object=parent_object)
            serializer_data = serializer.data
            '''
            Not doing this yet as I don't know how much info we want to give
            to someone about there info being flagged. I think we'll just want
            to notify them just not give them the person who did flag their
            content. We'll also need to allow them to provide a rebuttal.
            data = {
                "username": request.user.username,
                "flag": serializer_data['object_uuid'],
                "url": serializer_data['url'],
                "parent_object": self.kwargs[self.lookup_field]
            }
            spawn_task(task_func=create_flag_relations, task_param=data)
            '''
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
