from datetime import datetime

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from boto.dynamodb2.table import Table
from boto.dynamodb2.exceptions import JSONResponseError

from sb_docstore.utils import get_dynamo_table

from .serializers import SolutionSerializer
from .dynamo_table import SolutionModel


class QuestionSolutionList(ListAPIView):
    serializer_class = SolutionSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "parent_object"
    lookup_url_kwarg = "uuid"

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """

        table = get_dynamo_table("public_solutions")
        if isinstance(table, Exception) is True:
            return table
        print self.kwargs[self.lookup_url_kwarg]

        queryset = list(table.query_2(parent_object__eq=self.kwargs[
            self.lookup_url_kwarg]))
        print queryset
        filter = self.request.QUERY_PARAMS.get('filter', None)
        if filter == "created":
            queryset = sorted(
                queryset,
                key=lambda k: datetime.strptime(
                    k['time_created'][:len(k['time_created'])-6],
                    '%Y-%m-%d %H:%M:%S.%f'))
        elif filter == "edited":
            queryset = sorted(
                queryset,
                key=lambda k: datetime.strptime(
                    k['last_edited_on'][:len(k['last_edited_on'])-6],
                    '%Y-%m-%d %H:%M:%S.%f'))
        else:
            queryset = sorted(queryset, key=lambda k: k['object_vote_count'])
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(owner=self.request.user)