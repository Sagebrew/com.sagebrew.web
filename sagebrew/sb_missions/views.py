from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test


from sb_quests.neo_models import Position
from sb_registration.utils import (verify_completed_registration,
                                   verify_no_campaign)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def select_mission(request):
    if verify_no_campaign(request.user):
        return redirect('quest_saga', username=request.user.username)
    president = Position.nodes.get(name="President")
    return render(request, 'mission_selector.html',
                  {'president': president.object_uuid})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def public_office_mission(request):
    if verify_no_campaign(request.user):
        return redirect('quest_saga', username=request.user.username)
    president = Position.nodes.get(name="President")
    return render(request, 'public_office_mission.html',
                  {'president': president.object_uuid})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def advocate_mission(request):
    if verify_no_campaign(request.user):
        return redirect('quest_saga', username=request.user.username)
    president = Position.nodes.get(name="President")
    return render(request, 'advocate_mission.html',
                  {'president': president.object_uuid})
