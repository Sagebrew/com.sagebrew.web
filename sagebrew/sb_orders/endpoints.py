from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from sb_missions.neo_models import Mission

from .neo_models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_object(self):
        return Order.nodes.get(object_uuid=self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        mission_id = self.request.data['mission']
        mission = Mission.get(mission_id)
        serializer.save(mission=mission)

    def perform_update(self, serializer):
        mission_id = self.request.data['mission']
        mission = Mission.get(mission_id)
        quest = Mission.get_quest(object_uuid=mission_id)
        serializer.save(mission=mission, quest=quest)

    def list(self, request, *args, **kwargs):
        return Response({"details": "Sorry we don't allow users to query all "
                                    "Orders on the site.",
                         "status": status.HTTP_200_OK},
                        status=status.HTTP_200_OK)
