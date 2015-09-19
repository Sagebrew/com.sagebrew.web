from django.template.loader import render_to_string
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist, CypherException

from sb_registration.utils import (verify_completed_registration)

from .neo_models import PublicOfficial

from sb_campaigns.neo_models import PoliticalCampaign
from sb_campaigns.serializers import PoliticalCampaignSerializer


def saga(request, username):
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (CypherException, IOError, PublicOfficial.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    serializer_data = PoliticalCampaignSerializer(
        campaign, context={'request': request}).data
    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'action_page.html', serializer_data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def edit_epic(request, username):
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (CypherException, IOError, PublicOfficial.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    return render(request, 'edit_epic.html',
                  PoliticalCampaignSerializer(
                      campaign, context={'request': request}).data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def create_update(request, username):
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (CypherException, IOError, PublicOfficial.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    return render(request, 'create_update.html',
                  PoliticalCampaignSerializer(
                      campaign, context={'request': request}).data)


def updates(request, username):
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (CypherException, IOError, PublicOfficial.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    serializer_data = PoliticalCampaignSerializer(
        campaign, context={'request': request}).data
    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'action_page.html', serializer_data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def statistics(request, username):
    if request.user.username not in \
            PoliticalCampaign.get_campaign_helpers(username):
        return redirect('quest_saga', username)
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (CypherException, IOError, PublicOfficial.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    serializer_data = PoliticalCampaignSerializer(
        campaign, context={'request': request}).data

    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'action_page.html', serializer_data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def moderators(request, username):
    if not request.user.username == username:
        return redirect('quest_saga', username)
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (PublicOfficial.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    serializer_data = PoliticalCampaignSerializer(
        campaign, context={'request': request}).data

    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'action_page.html', serializer_data)


@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def get_search_html(request, object_uuid):
    try:
        campaign = PoliticalCampaign.get(object_uuid=object_uuid)
    except (CypherException, IOError):
        return Response('Server Error', status=500)
    rendered_html = render_to_string("saga_search_block.html",
                                     PoliticalCampaignSerializer(
                                         campaign,
                                         context={'request': request}).data)

    return Response({'html': rendered_html}, status=200)
