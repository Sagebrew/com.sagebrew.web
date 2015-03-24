from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from api.permissions import IsUser

from .models import SBApplication
from .serializers import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = SBApplication.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = 'client_id'
    permission_classes = (IsAdminUser, IsUser)
