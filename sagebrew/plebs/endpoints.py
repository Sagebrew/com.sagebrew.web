from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.permissions import IsSelfOrReadOnly

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)

    def retrieve(self, request, *args, **kwargs):
        single_object = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(single_object, context={
            'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
