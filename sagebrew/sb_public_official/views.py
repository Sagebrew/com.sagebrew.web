from django.template.loader import render_to_string
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist, CypherException

from sb_registration.utils import (verify_completed_registration)

from .neo_models import PublicOfficial

from sb_campaigns.neo_models import PoliticalCampaign
from sb_campaigns.serializers import PoliticalCampaignSerializer


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def saga(request, username):
    try:
        campaign = PoliticalCampaign.nodes.get(object_uuid=username)
    except (CypherException, IOError, PublicOfficial.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    return render(request, 'action_page.html',
                  PoliticalCampaignSerializer(campaign).data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def updates(request, username):
    try:
        campaign = PoliticalCampaign.nodes.get(object_uuid=username)
    except (CypherException, IOError, PublicOfficial.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    return render(request, 'action_page.html',
                  PoliticalCampaignSerializer(campaign).data)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_search_html(request, object_uuid):
    try:
        campaign = PoliticalCampaign.nodes.get(object_uuid=object_uuid)
    except (CypherException, IOError):
        return Response('Server Error', status=500)
    rendered_html = render_to_string("saga_search_block.html",
                                     PoliticalCampaignSerializer(
                                         campaign).data)

    return Response({'html': rendered_html}, status=200)
