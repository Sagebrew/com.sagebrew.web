from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test

from neomodel import DoesNotExist, CypherException

from sb_registration.utils import (verify_completed_registration)

from sb_public_official.neo_models import PublicOfficial

from sb_campaigns.neo_models import PoliticalCampaign
from sb_campaigns.serializers import PoliticalCampaignSerializer


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def manage_goals(request, username):
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (CypherException, IOError, PublicOfficial.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    return render(request, 'manage_goals.html',
                  PoliticalCampaignSerializer(
                      campaign, context={'request': request}).data)