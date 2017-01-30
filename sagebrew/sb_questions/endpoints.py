from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from api.utils import spawn_task
from sb_base.utils import get_ordering, get_tagged_as, NeoQuerySet
from sb_search.tasks import update_search_object

from .serializers import QuestionSerializerNeo, solution_count
from .neo_models import Question


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializerNeo
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # Tried a filtering class but it requires a order_by method to be defined
    # on the given queryset. Since django provides an actual QuerySet rather
    # than a plain list this works with the ORM but would require additional
    # implementation in neomodel. May be something we want to look into to
    # simplify the sorting logic in our queryset methods

    def get_queryset(self):
        sort_by = self.request.query_params.get('ordering', '')
        mission = self.request.query_params.get('mission', '')
        tagged_as = get_tagged_as(
            self.request.query_params.get('tagged_as', ''))
        sort_by, ordering = get_ordering(sort_by)
        mission_query = ''
        query = "(res:Question)%s" % tagged_as
        if ordering == "DESC":
            descending = True
        else:
            descending = False
        if mission:
            mission_query = '(m:Mission {object_uuid:"%s"})-' \
                            '[:ASSOCIATED_WITH]->' % mission
        if sort_by == "" or sort_by == "vote_count":
            query = "%s(res:Question)%s " \
                    "WHERE res.to_be_deleted=false " \
                    "OPTIONAL MATCH (res)<-[vs:PLEB_VOTES]-() " \
                    "WHERE vs.active=True " % (mission_query, tagged_as)
            queryset = NeoQuerySet(
                Question, query=query, distinct=True,
                descending=not descending)\
                .order_by(", reduce(vote_count = 0, v in collect(vs)| "
                          "CASE WHEN v.vote_type=True THEN vote_count+1 "
                          "WHEN v.vote_type=False THEN vote_count-1 "
                          "ELSE vote_count END) as reduce_res "
                          "ORDER BY reduce_res")
        else:
            queryset = NeoQuerySet(
                Question, query=query, distinct=True, descending=descending) \
                .filter('WHERE res.to_be_deleted=false') \
                .order_by(sort_by)
        # Quick cache implementation to reduce load of refresh clickers
        # Under load neo takes about 15-30 seconds to store off the
        # updates of a vote anyways so this can be added when necessary
        # if sort_by == "" or sort_by == "vote_count":
        #    if questions is None:
        #        cache.set('question_list_vote_sort', queryset, 30)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.get_paginated_response(
            self.get_serializer(
                self.paginate_queryset(queryset), many=True,
                context={"request": self.request}).data)

    def get_object(self):
        return Question.get(self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        if "tags" in request.data:
            if isinstance(request.data['tags'], basestring):
                request.data['tags'] = request.data['tags'].split(',')
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            instance = serializer.save(mission=request.data.get('mission', ''))
            spawn_task(task_func=update_search_object,
                       task_param={"object_uuid": instance.object_uuid,
                                   "label": "question"})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_object()
        single_object = QuestionSerializerNeo(
            queryset, context={'request': request, "expand_param": True}).data
        return Response(single_object, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def solution_count(self, request, object_uuid=None):
        count = solution_count(self.kwargs[self.lookup_field])
        return Response({"solution_count": count}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def close(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def protect(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)
