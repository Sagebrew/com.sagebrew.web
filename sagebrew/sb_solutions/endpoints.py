from datetime import datetime

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from sb_docstore.utils import get_dynamo_table
from sb_comments.utils import convert_dynamo_comments
from sb_comments.serializers import CommentSerializer

from .serializers import SolutionSerializer
from .utils import convert_dynamo_solution


class QuestionSolutionsList(ListAPIView):
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

        queryset = table.query_2(parent_object__eq=self.kwargs[
            self.lookup_url_kwarg])
        queryset = convert_dynamo_solution(queryset, self.request)
        sort_by = self.request.QUERY_PARAMS.get('sort_by', None)
        if sort_by == "created":
            queryset = sorted(
                queryset,
                key=lambda k: k['time_created'])
        elif sort_by == "edited":
            queryset = sorted(
                queryset,
                key=lambda k: k['last_edited_on'])
        else:
            queryset = sorted(queryset, key=lambda k: k['object_vote_count'])
        return queryset


class SolutionCommentList(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "parent_object"
    lookup_url_kwarg = "uuid"

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """

        table = get_dynamo_table("comments")
        if isinstance(table, Exception) is True:
            return table
        queryset = table.query_2(
            parent_object__eq=self.kwargs[self.lookup_url_kwarg],
            datetime__gte="0"
        )

        return convert_dynamo_comments(queryset)
