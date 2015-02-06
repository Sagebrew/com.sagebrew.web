from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sb_docstore.utils import get_action

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def check_action(request):
    print request.DATA
    res = get_action(request.user.username, request.DATA['action'])
    if isinstance(res, Exception):
        return Response({"detail": "fail"}, 400)
    if not res:
        return Response({"detail": "forbidden"}, 200)
    return Response(res, 200)
