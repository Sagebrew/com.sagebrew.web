from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string

from rest_framework.decorators import api_view, permission_classes, APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils import spawn_task
from sb_docstore.utils import get_action
from .utils import get_actions, get_requirements
from .tasks import (create_privilege_task, create_action_task,
                    create_requirement_task)
from .forms import (CheckActionForm, CreatePrivilegeForm, CreateActionForm,
                    CreateRequirementForm, SelectActionForm,
                    SelectRequirementForm)

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
        return Response({"html": render_to_string('action_form.html',
                                                  {"action_form":
                                                       CreateActionForm()},
                                                  context_instance=
                                                  RequestContext(request))},
                        200)

    def post(self, request, format=None):
        action_form = CreateActionForm(request.DATA)
        if action_form.is_valid():
            res = spawn_task(create_action_task, action_form.cleaned_data)
            if isinstance(res, Exception):
                return Response({"detail": "server error"}, 500)
            return Response({"detail": "success"}, 200)
        else:
            return Response({"detail": "invalid form",
                             "errors": action_form.errors}, 400)

class CreateRequirement(APIView):
    def get(self, request, format=None):
        return Response({"html": render_to_string('requirement_form.html',
            {"requirement_form": CreateRequirementForm()},
                                                  context_instance=
                                                  RequestContext(request))},
                        200)

    def post(self, request, format=None):
        req_form = CreateRequirementForm(request.DATA)
        if req_form.is_valid():
            res = spawn_task(create_requirement_task, req_form.cleaned_data)
            if isinstance(res, Exception):
                return Response({"detail": "server error"}, 500)
            return Response({"detail": "success"}, 200)
        else:
            return Response({"detail": "invalid form",
                             "errors": req_form.errors}, 400)

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

    def get(self, request, format=None):
        return Response({"html": render_to_string('privilege_choice.html',
            {'requirements': get_requirements(), 'actions': get_actions()},
            context_instance=RequestContext(request))}, 200)

    def post(self, request, format=None):
        print request.DATA
        action_forms = []
        requirement_forms = []
        privilege_form = CreatePrivilegeForm(
            {"privilege_name": request.DATA['privilege_name']})
        if privilege_form.is_valid():
            if 'actions' in request.DATA:
                if type(request.DATA['actions']) == list:
                    for action in request.DATA['actions']:
                        action_form = SelectActionForm({"object_uuid":action})
                        if action_form.is_valid():
                            action_forms.append(action_form.cleaned_data)
                        else:
                            return Response({"detail": "invalid action form",
                                             "errors": action_form.errors},
                                            400)
                else:
                    action_form = SelectActionForm(
                        {"object_uuid": request.DATA['actions']})
                    if action_form.is_valid():
                        action_forms.append(action_form.cleaned_data)
                    else:
                        return Response({"detail": "invalid action form",
                                         "errors": action_form.errors}, 400)
            if 'requirements' in request.DATA:
                if type(request.DATA['requirements']) == list:
                    for requirement in request.DATA['requirements']:
                        requirement_form = SelectActionForm(
                            {"object_uuid": requirement})
                        if requirement_form.is_valid():
                            requirement_forms.append(
                                requirement_form.cleaned_data)
                            return Response(
                                {"detail":"invalid requirement form",
                                "errors": requirement_form.errors})
                else:
                    requirement_form = SelectRequirementForm(
                        {"object_uuid": request.DATA['requirements']})
                    if requirement_form.is_valid():
                        requirement_forms.append(requirement_form.cleaned_data)
                        return Response({"detail":"invalid requirement form",
                                         "errors": requirement_form.errors})
            task_data = {
                "privilege_data": privilege_form.cleaned_data,
                "actions": action_forms,
                "requirements": requirement_forms
            }
            res = spawn_task(create_privilege_task, task_data)
            if isinstance(res, Exception):
                return Response({"detail": "server error"}, 500)
            return Response({"detail": "success"}, 200)
        else:
            return Response({"detail": "invalid privilege form",
                             "errors": privilege_form.errors}, 400)

