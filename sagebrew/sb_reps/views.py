import pytz
import logging
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.template import Template, RequestContext
from django.template.loader import render_to_string
from django.forms.formsets import formset_factory
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from sb_registration.utils import (verify_completed_registration)
from sb_docstore.utils import add_object_to_table, get_rep_docs
from sb_docstore.tasks import build_rep_page_task
from .forms import (AgendaForm, GoalForm, ExperienceForm, PolicyForm)
from .neo_models import BaseOfficial
from .tasks import save_policy_task, save_experience_task

@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def representative_page(request, rep_id=""):
    res = get_rep_docs(rep_id)
    if isinstance(res, Exception):
        return redirect('404_Error')
    if not res:
        policy_list = []
        experience_list = []
        spawn_task(build_rep_page_task, {"rep_id": rep_id})
        try:
            official = BaseOfficial.nodes.get(sb_id=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException):
            return redirect('profile_page', request.user.username)
        pleb = official.pleb.all()[0]
        name = pleb.first_name+' '+pleb.last_name
        full = official.title+pleb.first_name+' '+pleb.last_name
        username = pleb.username
        policies = official.policy.all()
        experiences = official.experience.all()
        for policy in policies:
            policy_list.append(policy.get_dict())
        for experience in experiences:
            experience_list.append(experience.get_dict())
        data = {
            "name": name,
            "full": full,
            "policies": policy_list,
            "experiences": experience_list, "username": username,
            "rep_id": rep_id
        }
        return render(request, 'rep_page.html', data)
    data = {
        'name': res['rep']['name'], 'full': res['rep']['full'],
        'policies': res['policies'], 'experiences': res['experiences'],
        'username': res['rep']['username'], 'rep_id': res['rep']['rep_id']
    }
    return render(request, 'rep_page.html', data)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_policies(request):
    pass

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def get_experience_form(request):
    experience_form = ExperienceForm(request.DATA or None)
    if request.method == 'POST':
        if experience_form.is_valid():
            rep_id = request.DATA['rep_id']
            uuid = str(uuid1())
            data = {'rep_id': rep_id,
                    'title': experience_form.cleaned_data['title'],
                    'start_date': experience_form.cleaned_data['start_date'],
                    'end_date': experience_form.cleaned_data['end_date'],
                    'current': experience_form.cleaned_data['current'],
                    'company': experience_form.cleaned_data['company'],
                    'location': experience_form.cleaned_data['location'],
                    'description': experience_form.cleaned_data['description'],
                    'exp_id': uuid}
            table_data = {'parent_object': str(id),
                    'title': experience_form.cleaned_data['title'],
                    'start_date': unicode(
                        experience_form.cleaned_data['start_date']),
                    'end_date': unicode(
                        experience_form.cleaned_data['end_date']),
                    'current': experience_form.cleaned_data['current'],
                    'company': experience_form.cleaned_data['company'],
                    'location': experience_form.cleaned_data['location'],
                    'description': experience_form.cleaned_data['description'],
                    'object_uuid': uuid}
            res = add_object_to_table('experiences', table_data)
            if isinstance(res, Exception):
                return Response({"detail": "error1"}, 400)
            res = spawn_task(save_experience_task, data)
            if isinstance(res, Exception):
                return Response({"detail": "error2"}, 400)
            rendered = render_to_string('experience_detail.html',
                                        {'experience': data})
            return Response({"detail": "success",
                             "rendered": rendered}, 200)
        else:
            return Response({"detail": "invalid form"}, 400)
    else:
        rendered = render_to_string('experience_form.html',
                                    {'experience_form': experience_form})
        return Response({"rendered": rendered}, 200)

@api_view(['GET','POST'])
@permission_classes((IsAuthenticated,))
def get_policy_form(request):
    policy_form = PolicyForm(request.DATA or None)
    if request.method == "POST":
        if policy_form.is_valid():
            rep_id = request.DATA['rep_id']
            data = {
                'rep_id': rep_id,
                'category': policy_form.cleaned_data['policies'],
                'description': policy_form.cleaned_data['description'],
                'object_uuid': str(uuid1())
            }
            res = spawn_task(save_policy_task, data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            data['parent_object'] = str(rep_id)
            res = add_object_to_table('policies', data)
            if isinstance(res, Exception):
                return Response({"detail": "error"}, 400)
            rendered = render_to_string('policy_detail.html', {'policy': data})
            return Response({"detail": "success",
                             "rendered": rendered}, 200)
    else:
        rendered = render_to_string('policy_form.html',
                          {'policy_form': policy_form})
        return Response({"rendered": rendered}, 200)