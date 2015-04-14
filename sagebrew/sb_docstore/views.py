from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response

from neomodel import CypherException

from api.utils import spawn_task
from sb_edits.tasks import edit_object_task
from sb_votes.tasks import vote_object_task
from sb_privileges.tasks import check_privileges
from plebs.neo_models import Pleb

from .utils import get_user_updates


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
        vote_res.append(get_user_updates(username=pleb.username,
                                         object_uuid=object_uuid,
                                         table_name='votes'))

    for item in vote_res:
        try:
            item['status'] = int(item['status'])
            task_data = {
                'vote_type': item['status'],
                'current_pleb': pleb,
                'object_uuid': item['parent_object'],
            }
            spawn_task(task_func=vote_object_task, task_param=task_data)
        except KeyError:
            pass
        spawn_task(task_func=check_privileges, task_param={
            "username": request.user.username})
    return Response({'detail': 'success'}, status=200)


