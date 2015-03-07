from django.shortcuts import render
from django.template.loader import render_to_string

from rest_framework.decorators import api_view, permission_classes, APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils import spawn_task
from sb_docstore.utils import get_action
from .tasks import create_privilege_task
from .forms import (CheckActionForm, CreatePrivilegeForm, CreateActionForm,
                    CreateRequirementForm)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def check_action(request):
    action_form = CheckActionForm(request.GET)
    if action_form.is_valid():
        res = get_action(request.user.username,
                         action_form.cleaned_data['action'])
        if isinstance(res, Exception):
            return Response({"detail": "fail"}, 400)
        if not res:
            return Response({"detail": "forbidden"}, 200)
        return Response(res, 200)
    else:
        return Response({'detail': 'invalid form'}, 400)

def create_privilege(request):
    privilege_form = CreatePrivilegeForm()
    action_form = CreateActionForm()
    requirement_form = CreateRequirementForm()
    return render(request, 'create_privilege.html',
                  {'privilege_form': privilege_form,
                   'action_form': action_form,
                   'requirement_form': requirement_form})

class CreateAction(APIView):
    def get(self, request, format=None):
        print request
        return Response({"html": render_to_string('action_form.html',
                                                  {"action_form":
                                                       CreateActionForm()})},
                        200)

class CreateRequirement(APIView):
    def get(self, request, format=None):
        return Response({"html": render_to_string('requirement_form.html',
            {"requirement_form": CreateRequirementForm()})}, 200)

class CreatePrivilege(APIView):
    def create_requirement(self, requirements):
        pass

    def create_action(self, actions):
        pass

    def create_privilege(self, privilege, actions, requirements):
        task_data = {
            'privilege_data': privilege,
            'actions': actions,
            'requirements': requirements
        }
        res = spawn_task(create_privilege_task, task_data)
        if isinstance(res, Exception):
            return False
        return True

    def post(self, request, format=None):
        print request.DATA
        action_forms = []
        requirement_forms = []
        privilege_form = CreatePrivilegeForm(request.DATA or None)
        if privilege_form.is_valid():
            for action in request.DATA['actions']:
                action_form =CreateActionForm(action)
                if action_form.is_valid():
                    action_forms.append(action_form.cleaned_data)
            for requirement in request.DATA['requirements']:
                requirement_form = CreateRequirementForm(requirement)
                if requirement_form.is_valid():
                    requirement_forms.append(requirement_form.cleaned_data)
        return Response({"detail": "success"}, 200)

