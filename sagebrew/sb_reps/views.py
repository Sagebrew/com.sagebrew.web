import pytz
import logging
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist, CypherException

from sb_registration.utils import (verify_completed_registration)
from .forms import (AgendaForm, GoalForm, ResumeForm, PolicyForm)
from .neo_models import BaseOfficial

@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def representative_page(request, rep_id=""):
    agenda_form = AgendaForm(request.POST or None)
    policy_form = PolicyForm(request.POST or None)
    resume_form = ResumeForm(request.POST or None)
    try:
        official = BaseOfficial.nodes.get(sb_id=rep_id)
    except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException):
        return redirect('profile_page', request.user.username)
    pleb = official.pleb.all()[0]
    data = {
        "name": pleb.first_name+' '+pleb.last_name,
        "full": official.title+pleb.first_name+' '+pleb.last_name,
        "policy": official.policies, "agenda": official.agenda,
        "resume": official.resume, "username": pleb.username,
        'agenda_form': agenda_form, 'policy_form': policy_form,
        'resume_form': resume_form,
    }

    return render(request, 'rep_page.html', data)