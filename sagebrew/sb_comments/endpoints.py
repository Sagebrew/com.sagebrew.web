from datetime import datetime
from logging import getLogger

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

from .neo_models import SBComment
from .serializers import CommentSerializer

logger = getLogger('loggly_logs')


class ObjectCommentsRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = CommentSerializer
    lookup_field = "object_uuid"
    lookup_url_kwarg = "comment_uuid"


class ObjectCommentsListCreate(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        query = "MATCH (a:SBContent {object_uuid:'%s'})-[:HAS_A]->" \
                "(b:SBComment) WHERE b.to_be_deleted=false" \
                " RETURN b ORDER BY b.created " \
                "DESC" % (self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return [SBComment.inflate(row[0]) for row in res]

    def create(self, request, *args, **kwargs):
        comment_data = request.data
        comment_data['parent_object'] = self.kwargs[self.lookup_field]
        serializer = self.get_serializer(data=comment_data)
        if serializer.is_valid():
            pleb = Pleb.nodes.get(username=request.user.username)
            parent_object = SBContent.nodes.get(
                object_uuid=self.kwargs[self.lookup_field])
            serializer.save(owner=pleb, parent_object=parent_object)

            """
            # This is more to what we'd like to do with the dynamo middleware
            serializer = CommentSerializer(instance,
                                           context={"request": request})
            put_item = dict(serializer.data)
            put_item['parent_object'] = parent_object.object_uuid
            table = get_dynamo_table("comments")
            table.put_item(data=put_item)
            """
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def comment_renderer(request, object_uuid=None):
    '''
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    '''
    html_array = []
    id_array = []
    args = []
    kwargs = {"object_uuid": object_uuid}
    comments = ObjectCommentsListCreate.as_view()(request, *args, **kwargs)
    for comment in comments.data['results']:
        comment['last_edited_on'] = datetime.strptime(
            comment[
                'last_edited_on'][:len(comment['last_edited_on']) - 6],
            '%Y-%m-%dT%H:%M:%S.%f')
        # This is a work around for django templates and our current
        # implementation of spacing for vote count in the template.
        comment["vote_count"] = str(comment["vote_count"])
        context = RequestContext(request, comment)
        html_array.append(render_to_string('sb_comments.html',  context))
        id_array.append(comment["object_uuid"])
    comments.data['results'] = {"html": html_array, "ids": id_array}
    return Response(comments.data, status=status.HTTP_200_OK)