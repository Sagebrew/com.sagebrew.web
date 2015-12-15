from django.utils.text import slugify
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from neomodel import db

from sb_registration.utils import (verify_completed_registration)

from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def select_mission(request):
    return render(request, 'mission_selector.html')


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def public_office_mission(request):
    return render(request, 'public_office_mission.html')


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def advocate_mission(request):
    return render(request, 'advocate_mission.html')


def mission_redirect_page(request, object_uuid):
    """
    This is the view that displays a single question with all solutions,
    comments,
    references and tags.

    :param request:
    :return:
    """
    mission_obj = Mission.get(object_uuid=object_uuid)
    if mission_obj.title:
        title = mission_obj.title
    else:
        if mission_obj.focus_name:
            title = mission_obj.focus_name.title()
        else:
            title = None
    return redirect("mission", object_uuid=object_uuid,
                    slug=slugify(title), permanent=True)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def mission(request, object_uuid, slug=None):
    query = 'MATCH (mission:Mission {object_uuid: "%s"}) ' \
            'RETURN mission' % object_uuid
    res, _ = db.cypher_query(query)
    if res.one is None:
        return redirect("404_Error")
    return render(request, 'mission.html',
                  MissionSerializer(Mission.inflate(res.one)).data)
