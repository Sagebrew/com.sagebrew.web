from datetime import datetime

from logging import getLogger

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView)

from neomodel import db

from sb_base.utils import get_ordering
from sb_base.views import ObjectRetrieveUpdateDestroy

from .serializers import SolutionSerializerNeo
from .neo_models import Solution


logger = getLogger('loggly_logs')


class SolutionViewSet(viewsets.ModelViewSet):
    serializer_class = SolutionSerializerNeo
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        sort_by = self.request.query_params.get('ordering', "")
        sort_by, ordering = get_ordering(sort_by)
        query = "MATCH (n:`Solution`) WHERE n.to_be_deleted=false RETURN " \
                "n %s %s" % (sort_by, ordering)
        res, col = db.cypher_query(query)
        queryset = [Solution.inflate(row[0]) for row in res]
        if sort_by == "":
            queryset = sorted(queryset, key=lambda k: k.get_vote_count(),
                              reverse=True)

        return queryset

    def get_object(self, object_uuid=None):
        return Solution.nodes.get(object_uuid=object_uuid)


class ObjectSolutionsRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = SolutionSerializerNeo
    lookup_field = "object_uuid"
    lookup_url_kwarg = "solution_uuid"

    def get_object(self):
        return Solution.nodes.get(
            object_uuid=self.kwargs[self.lookup_url_kwarg])


class ObjectSolutionsListCreate(ListCreateAPIView):
    serializer_class = SolutionSerializerNeo
    permission_classes = (IsAuthenticated,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        sort_by = self.request.query_params.get('ordering', "")
        sort_by, ordering = get_ordering(sort_by)
        query = "MATCH (a:Question {object_uuid:'%s'})-[:POSSIBLE_ANSWER]->" \
                "(b:Solution) WHERE b.to_be_deleted=false" \
                " RETURN b %s %s" % (self.kwargs[self.lookup_field],
                                     sort_by, ordering)
        res, col = db.cypher_query(query)
        queryset = [Solution.inflate(row[0]) for row in res]
        if sort_by == "":
            queryset = sorted(queryset, key=lambda k: k.get_vote_count(),
                              reverse=True)
        return queryset


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def solution_renderer(request, object_uuid=None):
    '''
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    '''
    html_array = []
    id_array = []
    args = []
    kwargs = {"object_uuid": object_uuid}
    solutions = ObjectSolutionsListCreate.as_view()(request, *args, **kwargs)
    for solution in solutions.data['results']:
        # This is a work around for django templates and our current
        # implementation of spacing for vote count in the template.
        solution["vote_count"] = str(solution["vote_count"])
        solution['last_edited_on'] = datetime.strptime(
            solution['last_edited_on'][:len(solution['last_edited_on']) - 6],
            '%Y-%m-%dT%H:%M:%S.%f')
        context = RequestContext(request, solution)
        html_array.append(render_to_string('solution.html',  context))
        id_array.append(solution["object_uuid"])
    solutions.data['results'] = {"html": html_array, "ids": id_array}

    return Response(solutions.data, status=status.HTTP_200_OK)