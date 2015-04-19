from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string

from .forms import RequirementForm


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def get_requirement_form(request):
    req_form = RequirementForm(request.DATA or None)
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        rendered = render_to_string("requirement_form.html",
                                    {"req_form": req_form})
        return Response({"rendered": rendered}, 200)
