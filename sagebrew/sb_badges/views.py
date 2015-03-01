from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string

from sb_registration.utils import (verify_completed_registration)

from .forms import CreateBadgeForm

@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def create_badge(request):
    form = CreateBadgeForm()
    return render(request, 'badge_creation.html', {'badge_form': form})

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_badge_api(request):
    pass