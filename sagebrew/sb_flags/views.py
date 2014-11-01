from json import dumps

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import FlagObjectForm

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def flag_object_view(request):
    flag_object_form = FlagObjectForm(request.DATA)
