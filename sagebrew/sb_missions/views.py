from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test


from sb_quests.neo_models import Position
from sb_registration.utils import (verify_completed_registration,
                                   verify_no_campaign)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def select_mission(request):
    return render(request, 'mission_selector.html', {})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def public_office_mission(request):
    return render(request, 'public_office_mission.html', {})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def advocate_mission(request):
    return render(request, 'advocate_mission.html', {})
