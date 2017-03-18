from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination

from sagebrew.api.permissions import IsAdminOrReadOnly

from sagebrew.sb_privileges.serializers import PrivilegeSerializer
from sagebrew.sb_privileges.neo_models import Privilege


class PrivilegeViewSet(viewsets.ModelViewSet):
    serializer_class = PrivilegeSerializer
    lookup_field = "name"
    queryset = Privilege.nodes.all()
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_object(self):
        return Privilege.nodes.get(name=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        """
        Currently a profile is generated for a user when the base user is
        created. We currently don't support creating a profile through an
        endpoint due to the confirmation process and links that need to be
        made.
        :param request:
        :return:
        """
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def solutions(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)
