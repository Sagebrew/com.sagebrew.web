from datetime import datetime
from logging import getLogger

from django.core.cache import cache
from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.decorators import (api_view, permission_classes)
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

logger = getLogger('loggly_logs')


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
            html = request.query_params.get('html', 'false').lower()
            if html == "true":
                serializer_data["vote_count"] = str(
                    serializer_data["vote_count"])
                serializer_data['last_edited_on'] = datetime.strptime(
                    serializer_data['last_edited_on'][:len(
                        serializer_data['last_edited_on']) - 6],
                    '%Y-%m-%dT%H:%M:%S.%f')
                context = RequestContext(request, serializer_data)
                return Response(
                    {
                        "html": [render_to_string('comment.html', context)],
                        "ids": [serializer_data["object_uuid"]]
                    },
                    status=status.HTTP_200_OK)
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def flag_renderer(request, object_uuid=None):
    """
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    """
    html_array = []
    id_array = []
    args = []
    kwargs = {"object_uuid": object_uuid}
    comments = ObjectFlagsListCreate.as_view()(request, *args, **kwargs)
    for comment in comments.data['results']:
        comment['last_edited_on'] = datetime.strptime(
            comment[
                'last_edited_on'][:len(comment['last_edited_on']) - 6],
            '%Y-%m-%dT%H:%M:%S.%f')
        # This is a work around for django templates and our current
        # implementation of spacing for vote count in the template.
        comment["vote_count"] = str(comment["vote_count"])
        context = RequestContext(request, comment)
        html_array.append(render_to_string('comment.html', context))
        id_array.append(comment["object_uuid"])
    comments.data['results'] = {"html": html_array, "ids": id_array}
    return Response(comments.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def flag_list(request):
    response = {
        "status": status.HTTP_501_NOT_IMPLEMENTED,
        "detail": "We do not allow users to query all the Flags on the site.",
        "developer_message":
            "We're working on enabling easier access to flags based."
            "However this endpoint currently does not return any "
            "flag data. Please use the other content endpoints to "
            "reference the flags on them."
    }
    return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)
