from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response

from neomodel import CypherException

from .utils import get_user_updates
from api.utils import spawn_task
from sb_edits.tasks import edit_object_task
from sb_votes.tasks import vote_object_task
from plebs.neo_models import Pleb

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def get_updates_from_dynamo(request):
    edit_res = []
    vote_res = []
    try:
        pleb = Pleb.nodes.get(username=request.user.username)
    except CypherException:
        return Response(status=500)
    for object_uuid in request.DATA['object_uuids']:
        edit_res.append(get_user_updates(username=pleb.email,
                                        object_uuid=object_uuid,
                                        table_name='edits'))
        vote_res.append(get_user_updates(username=pleb.email,
                                        object_uuid=object_uuid,
                                        table_name='votes'))
    for item in edit_res:
        for edit in item:
            task_data = {
                'object_uuid': edit['parent_object'],
                'object_type': edit['object_type'],
                'current_pleb': pleb,
                'content': edit['content']
            }
            spawn_task(task_func=edit_object_task, task_param=task_data)

    for item in vote_res:
        try:
            item['status'] = int(item['status'])
            task_data = {
                'vote_type': item['status'],
                'current_pleb': pleb,
                'object_uuid': item['parent_object'],
                'object_type': item['object_type']
            }
            spawn_task(task_func=vote_object_task, task_param=task_data)
        except KeyError:
            pass
    return Response({'detail': 'success'}, status=200)


