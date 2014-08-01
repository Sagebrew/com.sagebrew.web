from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from plebs.neo_models import Pleb


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_notification(request):
    pass


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_notifications(request):
    citizen = Pleb.index.get(email=request.DATA['email'])
    notifications = citizen.traverse('notifications').where('seen', '=',
                                                            False).run()
    return Response(notifications, status=200)






