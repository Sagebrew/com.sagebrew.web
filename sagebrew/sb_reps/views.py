import pytz
import logging
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.forms.formsets import formset_factory
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from sb_registration.utils import (verify_completed_registration)
from sb_docstore.utils import get_policies
from .forms import (AgendaForm, GoalForm, ResumeForm, PolicyForm)
from .neo_models import BaseOfficial
from .tasks import save_policy_task

@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def representative_page(request, rep_id=""):
    agenda_form = AgendaForm(request.POST or None)
    resume_form = ResumeForm(request.POST or None)
    PolicyFormSet = formset_factory(PolicyForm)
    policy_form_set = PolicyFormSet(request.POST or None, prefix='policy')
    if policy_form_set.is_valid():
        for item in policy_form_set:
            data = {
                'rep_id': rep_id,
                'category': item.cleaned_data['policies'],
                'description': item.cleaned_data['description'],
                'object_uuid': str(uuid1())
            }
            spawn_task(save_policy_task, data)
    try:
        official = BaseOfficial.nodes.get(sb_id=rep_id)
    except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException):
        return redirect('profile_page', request.user.username)
    res = get_policies(rep_id)
    pleb = official.pleb.all()[0]
    data = {
        "name": pleb.first_name+' '+pleb.last_name,
        "full": official.title+pleb.first_name+' '+pleb.last_name,
        "policies": res, "agenda": official.agenda,
        "resume": official.resume, "username": pleb.username,
        'agenda_form': agenda_form, 'policy_form_set': policy_form_set,
        'resume_form': resume_form,
    }

    return render(request, 'rep_page.html', data)