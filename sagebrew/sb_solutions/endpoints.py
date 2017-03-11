from uuid import uuid1

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import (viewsets, status)
from rest_framework.response import Response
from rest_framework.generics import (ListCreateAPIView)
from rest_framework.reverse import reverse

from neomodel import db

from sagebrew.api.utils import spawn_task
from sagebrew.sb_notifications.tasks import spawn_notifications
from sagebrew.sb_base.utils import get_ordering, NeoQuerySet
from sagebrew.sb_base.views import ObjectRetrieveUpdateDestroy
from sagebrew.sb_questions.neo_models import Question
from sagebrew.plebs.neo_models import Pleb

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
        if ordering == "DESC":
            descending = True
        else:
            descending = False
        if sort_by == "" or sort_by == "vote_count":
            query = "(q:Question {object_uuid: '%s'})-" \
                    "[:POSSIBLE_ANSWER]->(res:Solution) " \
                    "WHERE res.to_be_deleted=false " \
                    "OPTIONAL MATCH (res)<-[vs:PLEB_VOTES]-() " \
                    "WHERE vs.active=True" % self.kwargs[self.lookup_field]
            reduce_query = ", reduce(vote_count = 0, v in collect(vs)|" \
                           "CASE WHEN v.vote_type=True THEN vote_count+1 " \
                           "WHEN v.vote_type=False THEN vote_count-1 " \
                           "ELSE vote_count END) as reduction " \
                           "ORDER BY reduction"
            return NeoQuerySet(Solution, query=query,
                               distinct=True,
                               descending=not descending).order_by(reduce_query)
        else:
            query = "(a:Question {object_uuid:'%s'})-" \
                    "[:POSSIBLE_ANSWER]->" \
                    "(res:Solution)" % self.kwargs[self.lookup_field]
            return NeoQuerySet(Solution, query=query, distinct=True,
                               descending=descending)\
                .filter("WHERE res.to_be_deleted=false")\
                .order_by(sort_by)

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
            to_plebs = [question_owner.username]
            mission = question.get_mission(question.object_uuid)
            if mission:
                to_plebs.append(mission['owner_username'])
            spawn_task(task_func=spawn_notifications, task_param={
                "from_pleb": request.user.username,
                "sb_object": serializer['object_uuid'],
                "url": reverse(
                    'single_solution_page',
                    kwargs={"object_uuid": serializer["object_uuid"]}),
                # TODO discuss notifying all the people who have provided
                # solutions on a given question.
                "to_plebs": to_plebs,
                "notification_id": str(uuid1()),
                'action_name': instance.action_name
            })
            # Not going to add until necessary for search
            # spawn_task(task_func=add_solution_to_search_index,
            #            task_param={"solution": serializer})
            return Response(serializer, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
