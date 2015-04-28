from boto.dynamodb2.exceptions import (JSONResponseError)

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response

from api.utils import spawn_task
from sb_votes.tasks import vote_object_task

from .utils import get_user_updates


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def get_updates_from_dynamo(request):
    vote_res = []
    for object_uuid in request.DATA['object_uuids']:
        try:
            vote_res.append(get_user_updates(username=request.user.username,
                                             object_uuid=object_uuid,
                                             table_name='votes'))
        except JSONResponseError:
            return Response({'detail': 'Failed to connect to datastore'},
                            status=500)

    for item in vote_res:
        try:
            item['status'] = int(item['status'])
            task_data = {
                'vote_type': item['status'],
                'current_pleb': request.user.username,
                'object_uuid': item['parent_object'],
            }
            spawn_task(task_func=vote_object_task, task_param=task_data)
        except KeyError:
            pass
    return Response({'detail': 'success'}, status=200)
