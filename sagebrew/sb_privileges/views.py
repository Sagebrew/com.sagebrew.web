from django.shortcuts import render

from rest_framework.decorators import APIView
from rest_framework.response import Response

from api.utils import spawn_task

from .tasks import (create_privilege_task)
from .forms import (CreatePrivilegeForm, CreateActionForm,
                    CreateRequirementForm, SelectActionForm,
                    SelectRequirementForm)


def create_privilege(request):
    privilege_form = CreatePrivilegeForm()
    action_form = CreateActionForm()
    requirement_form = CreateRequirementForm()
    return render(request, 'create_privilege.html',
                  {'privilege_form': privilege_form,
                   'action_form': action_form,
                   'requirement_form': requirement_form})


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
        action_forms = []
        requirement_forms = []
        privilege_form = CreatePrivilegeForm(
            {"name": request.DATA['name']})
        if privilege_form.is_valid():
            if 'actions' in request.DATA:
                if type(request.DATA['actions']) == list:
                    for action in request.DATA['actions']:
                        action_form = SelectActionForm({"object_uuid": action})
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
                            return Response({
                                "detail": "invalid requirement form",
                                "errors": requirement_form.errors
                            })
                else:
                    requirement_form = SelectRequirementForm(
                        {"object_uuid": request.DATA['requirements']})
                    if requirement_form.is_valid():
                        requirement_forms.append(requirement_form.cleaned_data)
                        return Response({"detail": "invalid requirement form",
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
            return Response({
                "detail": "invalid privilege form",
                "errors": privilege_form.errors
            }, 400)
