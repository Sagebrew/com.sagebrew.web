from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response

from api.utils import spawn_task
from .tasks import spawn_user_updates


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def get_updates_from_dynamo(request):
    spawn_task(task_func=spawn_user_updates, task_param={
        'username': request.user.username,
        "object_uuids": request.data['object_uuids']})

    return Response({'detail': 'success'}, status=200)
