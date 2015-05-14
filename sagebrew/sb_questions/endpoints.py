from datetime import datetime
from logging import getLogger

from django.template.loader import render_to_string
from django.template import RequestContext

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import status

from neomodel import db

from api.utils import spawn_task
from sb_base.utils import get_ordering, get_tagged_as
from sb_stats.tasks import update_view_count_task

from .serializers import QuestionSerializerNeo, solution_count
from .neo_models import Question
from .tasks import add_question_to_indices_task

logger = getLogger('loggly_logs')


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializerNeo
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)
    # Tried a filtering class but it requires a order_by method to be defined
    # on the given queryset. Since django provides an actual QuerySet rather
    # than a plain list this works with the ORM but would require additional
    # implementation in neomodel. May be something we want to look into to
    # simplify the sorting logic in our queryset methods

    def get_queryset(self):
        sort_by = self.request.query_params.get('ordering', '')
        tagged_as = get_tagged_as(
            self.request.query_params.get('tagged_as', ''))
        sort_by, ordering = get_ordering(sort_by)
        query = "MATCH (n:`Question`)%s WHERE n.to_be_deleted=false RETURN " \
                "n %s %s" % (tagged_as, sort_by, ordering)
        if sort_by == "" or sort_by == "vote_count":
            query = "MATCH (n:`Question`)%s " \
                    "OPTIONAL MATCH (n:`Question`)-[vs:PLEB_VOTES]-() " \
                    "WHERE n.to_be_deleted=false RETURN " \
                    "n, reduce(vote_count = 0, v in collect(vs)| " \
                    "CASE WHEN v.active=false THEN vote_count " \
                    "WHEN v.vote_type=True THEN vote_count+1 " \
                    "WHEN v.vote_type=False THEN vote_count-1  " \
                    "ELSE vote_count END) as reduction " \
                    "ORDER BY reduction DESC" % \
                    (tagged_as)
        res, col = db.cypher_query(query)
        queryset = [Question.inflate(row[0]) for row in res]
        return queryset

    def get_object(self):
        return Question.get(self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        request_data = request.data
        if "tags" in request_data:
            if isinstance(request_data['tags'], basestring):
                request_data['tags'] = request_data['tags'].split(',')
        serializer = self.get_serializer(data=request.data,
                                         context={"request": request})
        if serializer.is_valid():
            serializer.save()
            serializer = serializer.data
            spawn_task(task_func=add_question_to_indices_task,
                       task_param={"question": serializer})
            html = request.query_params.get('html', 'false').lower()
            if html == "true":
                serializer["vote_count"] = str(serializer["vote_count"])
                serializer['last_edited_on'] = datetime.strptime(
                    serializer['last_edited_on'][:-6], '%Y-%m-%dT%H:%M:%S.%f')
                context = RequestContext(request, serializer)
                return Response(
                    {
                        "html": [render_to_string('solution.html', context)],
                        "ids": [serializer["object_uuid"]]
                    },
                    status=status.HTTP_200_OK)

            return Response(serializer, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        html = self.request.query_params.get('html', 'false').lower()

        queryset = self.get_object()
        single_object = QuestionSerializerNeo(
            queryset, context={'request': request}).data

        if html == "true":
            spawn_task(update_view_count_task,
                       {'object_uuid': queryset.object_uuid,
                        'username': request.user.username})
            single_object["last_edited_on"] = datetime.strptime(
                single_object['last_edited_on'][:-6], '%Y-%m-%dT%H:%M:%S.%f')
            # This will be moved to JS Framework but don't need intermediate
            # step at the time being as this doesn't require pagination
            context = RequestContext(request, single_object)
            return Response({"html": render_to_string('question.html', context),
                             "ids": [single_object["object_uuid"]],
                             "solution_count": single_object['solution_count']},
                            status=status.HTTP_200_OK)

        return Response(single_object, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def solution_count(self, request, object_uuid=None):
        count = solution_count(self.kwargs[self.lookup_field])
        return Response({"solution_count": count}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def upvote(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def downvote(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def close(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def protect(self, request, object_uuid=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @list_route(methods=['get'])
    def render(self, request):
        """
        This is a intermediate step on the way to utilizing a JS Framework to
        handle template rendering.
        """
        html_array = []
        id_array = []
        questions = self.list(request)

        for question in questions.data['results']:
            # This is a work around for django templates and our current
            # implementation of spacing for vote count in the template.
            question["vote_count"] = str(question["vote_count"])
            question['last_edited_on'] = datetime.strptime(
                question['last_edited_on'][:-6], '%Y-%m-%dT%H:%M:%S.%f')
            context = RequestContext(request, question)
            html_array.append(render_to_string('question_summary.html',
                                               context))
            id_array.append(question["object_uuid"])
        questions.data['results'] = {"html": html_array, "ids": id_array}
        return Response(questions.data, status=status.HTTP_200_OK)
