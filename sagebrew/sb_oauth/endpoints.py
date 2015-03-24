from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.reverse import reverse
from rest_framework.response import Response

from .models import PSApplication
from .serializers import ApplicationSerializer, StorefrontSerializer


@api_view(('GET',))
def registration_root(request, format=None):
    return Response({
        'owners': reverse('users-list', request=request,
                          format=format),
    })


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = PSApplication.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = 'client_id'
    permission_classes = (IsAuthenticated, IsAdminUser)


class StorefrontViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = StorefrontSerializer
    lookup_field = 'username'

    permission_classes = (IsAuthenticated, IsAdminUser)

