from logging import getLogger
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication

from rest_framework import status
from rest_framework.response import Response

from sagebrew.sb_accounting.serializers import AccountSerializer

logger = getLogger("loggly_logs")


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class AccountingViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (AllowAny, )
    serializer_class = AccountSerializer

    def get_queryset(self):
        # TODO after verifying this works in staging we can change this back
        # to a property being set with an empty list.
        return []

    def create(self, request, *args, **kwargs):
        # TODO after this is verified on staging we can remove this completely
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request})
        if serializer.is_valid():
            self.perform_create(serializer)
        else:
            logger.critical(serializer.errors)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)
