from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny

from .serializers import AccountSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class AccountingViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (AllowAny, )
    serializer_class = AccountSerializer
    queryset = []
