from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from api.permissions import IsSelfOrReadOnly

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    permission_classes = (IsAdminUser, IsSelfOrReadOnly)


