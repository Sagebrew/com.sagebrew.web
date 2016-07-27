from django.conf import settings

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from neomodel import db


class GiftListViewSet(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)
