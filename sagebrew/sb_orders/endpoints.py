from django.conf import settings

from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from sagebrew.sb_base.utils import NeoQuerySet
from sagebrew.sb_base.serializers import IntercomMessageSerializer
from sagebrew.sb_missions.neo_models import Mission
from sagebrew.plebs.neo_models import Pleb

from .neo_models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        if query_params.get("completed") == "true":
            query = "(res:Order {paid: true, completed: true})"
        else:
            query = "(res:Order {paid: true, completed: false})"
        return NeoQuerySet(
            Order, query=query, distinct=True, descending=True)\
            .order_by('ORDER BY res.created')

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
        if request.user.username != "tyler_wiersing" \
                and request.user.username != "devon_bleibtrey":
            return Response({"details": "Sorry we don't allow users "
                                        "to query all "
                                        "Orders on the site.",
                             "status": status.HTTP_403_FORBIDDEN},
                            status=status.HTTP_403_FORBIDDEN)
        return super(OrderViewSet, self).list(request, *args, **kwargs)

    @detail_route(methods=['POST'],
                  permission_classes=[IsAuthenticated, ],
                  serializer_class=OrderSerializer)
    def complete_order(self, request, object_uuid=None):
        if request.user.username != "tyler_wiersing" \
                and request.user.username != "devon_bleibtrey":
            return Response({"detail": "You do not have permission to "
                                       "perform this action.",
                             "status_code": status.HTTP_403_FORBIDDEN},
                            status=status.HTTP_403_FORBIDDEN)
        order = self.get_object()
        tracking_url = request.data.get("tracking_url", None)
        if tracking_url:
            order.tracking_url = tracking_url
            order.completed = True
            order.save()
            order_owner = Pleb.get(order.owner_username)
            message_data = {
                'message_type': 'email',
                'subject': 'Sagebrew Order Processed',
                'body': 'Hi %s,\nYour Order has been processed and you '
                        'can track the delivery here:\n\n%s '
                        % (order_owner.first_name, tracking_url),
                'template': "personal",
                'from_user': {
                    'type': "admin",
                    'id': settings.INTERCOM_ADMIN_ID_DEVON},
                'to_user': {
                    'type': "user",
                    'user_id': order.owner_username}
            }
            serializer = IntercomMessageSerializer(data=message_data)
            if serializer.is_valid():
                serializer.save()

            mission = order.get_mission()
            mission_owner = Pleb.get(mission.owner_username)
            message_data = {
                'message_type': 'email',
                'subject': 'Someone has given you a Gift!',
                'body': 'Hi %s,\nSomeone has sent you a Gift from your '
                        'Giftlist!\nYou can track the delivery here:\n\n'
                        '%s'
                        % (mission_owner.first_name, tracking_url),
                'template': "personal",
                'from_user': {
                    'type': "admin",
                    'id': settings.INTERCOM_ADMIN_ID_DEVON},
                'to_user': {
                    'type': "user",
                    'user_id': mission.owner_username}
            }
            serializer = IntercomMessageSerializer(data=message_data)
            if serializer.is_valid():
                serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
