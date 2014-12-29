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
from sb_docstore.utils import get_rep_info, add_object_to_table
from .forms import (AgendaForm, GoalForm, ExperienceForm, PolicyForm)
from .neo_models import BaseOfficial
from .tasks import save_policy_task, save_experience_task

@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def representative_page(request, rep_id=""):
    agenda_form = AgendaForm(request.POST or None)
    try:
        official = BaseOfficial.nodes.get(sb_id=rep_id)
    except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException):
        return redirect('profile_page', request.user.username)
    res = get_rep_info(rep_id, 'policies')
    exp = get_rep_info(rep_id, 'experiences')
    pleb = official.pleb.all()[0]
    data = {
        "name": pleb.first_name+' '+pleb.last_name,
        "full": official.title+pleb.first_name+' '+pleb.last_name,
        "policies": res, "agenda": official.agenda,
        "experiences": exp, "username": pleb.username,
        'agenda_form': agenda_form,
        "rep_id": rep_id
    }

    return render(request, 'rep_page.html', data)

@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def get_experience_form(request):
    experience_form = ExperienceForm(request.DATA or None)
    if request.method == 'POST':
        if experience_form.is_valid():
            id = request.DATA['rep_id']
            uuid = str(uuid1())
            data = {'rep_id': id,
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
            return Response({"detail": "success"}, 200)
        else:
            return Response({"detail": "invalid form"}, 400)
    else:
        rendered = render_to_string('experience_form.html',
                                    {'experience_form': experience_form})
        return Response({"rendered": rendered}, 200)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_policy_form(request):
    PolicyFormSet = formset_factory(PolicyForm)
    policy_form_set = PolicyFormSet(request.POST or None, prefix='policy')
    if policy_form_set.is_valid():
        for item in policy_form_set:
            data = {
                'rep_id': request.user.email,
                'category': item.cleaned_data['policies'],
                'description': item.cleaned_data['description'],
                'object_uuid': str(uuid1())
            }
            spawn_task(save_policy_task, data)
    rendered = render(request, 'policy_form.html',
                      {'policy_form_set': policy_form_set})
    print rendered