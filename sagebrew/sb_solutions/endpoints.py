from uuid import uuid1
from dateutil import parser

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import (viewsets, status)
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response
from rest_framework.generics import (ListCreateAPIView)
from rest_framework.reverse import reverse

from neomodel import db

from api.utils import spawn_task
from sb_notifications.tasks import spawn_notifications
from sb_base.utils import get_ordering
from sb_base.views import ObjectRetrieveUpdateDestroy
from sb_questions.neo_models import Question
from plebs.neo_models import Pleb

from .serializers import SolutionSerializerNeo
from .neo_models import Solution


class SolutionViewSet(viewsets.ModelViewSet):
    serializer_class = SolutionSerializerNeo
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        sort_by = self.request.query_params.get('ordering', "")
        sort_by, ordering = get_ordering(sort_by)
        query = "MATCH (n:`Solution`) WHERE n.to_be_deleted=false RETURN " \
                "n %s %s" % (sort_by, ordering)
        res, col = db.cypher_query(query)
        [row[0].pull() for row in res]
        queryset = [Solution.inflate(row[0]) for row in res]
        if sort_by == "":
            queryset = sorted(queryset, key=lambda k: k.get_vote_count(),
                              reverse=True)

        return queryset

    def get_object(self):
        return Solution.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance).data
        html = request.query_params.get('html', 'false').lower()
        if html == 'true':
            serializer['last_edited_on'] = parser.parse(
                serializer['last_edited_on']).replace(microsecond=0)
            serializer['created'] = parser.parse(
                serializer['created']).replace(microsecond=0)
            return Response(
                {"html": render_to_string(
                    "solution.html", RequestContext(request, serializer)),
                 "id": instance.object_uuid,
                 "results": serializer},
                status=status.HTTP_200_OK)
        return Response(serializer)

    def perform_destroy(self, instance):
        instance.content = ""
        instance.to_be_deleted = True
        instance.save()
        return instance


class ObjectSolutionsRetrieveUpdateDestroy(ObjectRetrieveUpdateDestroy):
    serializer_class = SolutionSerializerNeo
    lookup_field = "object_uuid"
    lookup_url_kwarg = "solution_uuid"

    def get_object(self):
        return Solution.nodes.get(
            object_uuid=self.kwargs[self.lookup_url_kwarg])


class ObjectSolutionsListCreate(ListCreateAPIView):
    serializer_class = SolutionSerializerNeo
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = "object_uuid"

    def get_queryset(self):
        sort_by = self.request.query_params.get('ordering', "")
        sort_by, ordering = get_ordering(sort_by)
        if sort_by == "" or sort_by == "vote_count":
            query = "MATCH (q:Question {object_uuid: '%s'})-" \
                    "[:POSSIBLE_ANSWER]->(b:Solution) " \
                    "WHERE b.to_be_deleted=false " \
                    "OPTIONAL MATCH (b)<-[vs:PLEB_VOTES]-() " \
                    "WHERE vs.active=True " \
                    "RETURN b, reduce(vote_count = 0, v in collect(vs)|" \
                    "CASE WHEN v.vote_type=True THEN vote_count+1 " \
                    "WHEN v.vote_type=False THEN vote_count-1 " \
                    "ELSE vote_count END) as reduction " \
                    "ORDER BY reduction DESC" % (self.kwargs[self.lookup_field])
        else:
            query = "MATCH (a:Question {object_uuid:'%s'})-" \
                    "[:POSSIBLE_ANSWER]->" \
                    "(b:Solution) WHERE b.to_be_deleted=false" \
                    " RETURN b %s %s" % (self.kwargs[self.lookup_field],
                                         sort_by, ordering)
        res, col = db.cypher_query(query)
        return res

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        [row[0].pull() for row in page]
        page = [Solution.inflate(row[0]) for row in page]
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            question = Question.nodes.get(
                object_uuid=self.kwargs[self.lookup_field])
            instance = serializer.save(question=question)
            query = "MATCH (a:Question {object_uuid:'%s'})-[:OWNED_BY]->" \
                    "(b:Pleb) RETURN b" % (self.kwargs[self.lookup_field])
            res, col = db.cypher_query(query)
            question_owner = Pleb.inflate(res[0][0])
            serializer = serializer.data
            spawn_task(task_func=spawn_notifications, task_param={
                "from_pleb": request.user.username,
                "sb_object": serializer['object_uuid'],
                "url": reverse(
                    'single_solution_page',
                    kwargs={"object_uuid": serializer["object_uuid"]}),
                # TODO discuss notifying all the people who have provided
                # solutions on a given question.
                "to_plebs": [question_owner.username, ],
                "notification_id": str(uuid1()),
                'action_name': instance.action_name
            })
            # Not going to add until necessary for search
            # spawn_task(task_func=add_solution_to_search_index,
            #            task_param={"solution": serializer})
            if request.query_params.get('html', 'false').lower() == "true":
                serializer['last_edited_on'] = parser.parse(
                    serializer['last_edited_on']).replace(microsecond=0)
                serializer['created'] = parser.parse(
                    serializer['created']).replace(microsecond=0)
                return Response(
                    {
                        "html": [render_to_string(
                            'solution.html',
                            RequestContext(request, serializer))],
                        "ids": [serializer["object_uuid"]]
                    },
                    status=status.HTTP_200_OK)
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticatedOrReadOnly,))
def solution_renderer(request, object_uuid=None):
    """
    This is a intermediate step on the way to utilizing a JS Framework to
    handle template rendering.
    """
    html_array = []
    id_array = []
    solutions = ObjectSolutionsListCreate.as_view()(
        request, object_uuid=object_uuid)
    for solution in solutions.data['results']:
        solution['last_edited_on'] = parser.parse(
            solution['last_edited_on']).replace(microsecond=0)
        solution['created'] = parser.parse(
            solution['created']).replace(microsecond=0)
        html_array.append(render_to_string(
            'solution.html', RequestContext(request, solution)))
        id_array.append(solution["object_uuid"])
    solutions.data['results'] = {"html": html_array, "ids": id_array}

    return Response(solutions.data, status=status.HTTP_200_OK)
