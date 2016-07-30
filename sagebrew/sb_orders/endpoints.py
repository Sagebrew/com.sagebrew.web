from rest_framework.response import Response
from rest_framework import status, viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from neomodel import db

from sb_missions.neo_models import Mission
from sb_quests.neo_models import Quest
from plebs.neo_models import Pleb

from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
