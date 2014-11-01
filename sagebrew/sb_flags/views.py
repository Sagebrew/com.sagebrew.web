from json import dumps
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist

from .forms import FlagObjectForm
from .tasks import flag_object_task
from plebs.neo_models import Pleb
from api.utils import get_object, spawn_task

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def flag_object_view(request):
    flag_object_form = FlagObjectForm(request.DATA)
    if flag_object_form.is_valid():
        try:
            pleb = Pleb.nodes.get(email=flag_object_form.
                                  cleaned_data['current_pleb'])
        except (Pleb.DoesNotExist, DoesNotExist):
            return Response({"detail": "pleb does not exist"}, status=401)

        sb_object = get_object(flag_object_form.cleaned_data['object_type'],
                               flag_object_form.cleaned_data['object_uuid'])
        if not object:
            return Response({"detail": "object does not exist"})

