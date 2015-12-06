from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test

from neomodel import DoesNotExist, CypherException

from sb_registration.utils import (verify_completed_registration)

from api.utils import smart_truncate
from sb_quests.neo_models import PoliticalCampaign, Quest
from sb_quests.serializers import PoliticalCampaignSerializer, QuestSerializer


def quest(request, username):
    try:
        quest = Quest.get(object_uuid=username)
    except (CypherException, IOError, PoliticalCampaign.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    serializer_data = QuestSerializer(
        quest, context={'request': request}).data
    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    serializer_data['description'] = "%s %s's Policies, Agenda, " \
                                     "and Platform." % (
        serializer_data['first_name'], serializer_data['last_name'])
    serializer_data['keywords'] = "Politics, Fundraising, Campaign, Quest,"
    return render(request, 'quest.html', serializer_data)


def saga(request, username):
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (CypherException, IOError, PoliticalCampaign.DoesNotExist,
            DoesNotExist):
        return redirect("404_Error")
    serializer_data = PoliticalCampaignSerializer(
        campaign, context={'request': request}).data
    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    if serializer_data['biography'] is not None:
        serializer_data['description'] = smart_truncate(
            serializer_data['biography'], length=150)
    else:
        serializer_data['description'] = "%s %s's Policies, Agenda, " \
                                         "and Platform." % (
            serializer_data['first_name'], serializer_data['last_name'])
    serializer_data['keywords'] = "Politics, Fundraising, Campaign, Quest," \
                                  " Candidate, " \
                                  "Representative, %s, %s, %s" % (
        serializer_data['position_formal_name'],
        serializer_data['location_name'], serializer_data['position_name'])
    return render(request, 'saga.html', serializer_data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def edit_epic(request, username):
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (PoliticalCampaign.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    return render(request, 'edit_epic.html',
                  PoliticalCampaignSerializer(
                      campaign, context={'request': request}).data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def insights(request, username):
    if request.user.username not in \
            PoliticalCampaign.get_campaign_helpers(username):
        return redirect('quest_saga', username)
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (PoliticalCampaign.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    serializer_data = PoliticalCampaignSerializer(
        campaign, context={'request': request}).data
    serializer_data['description'] = "Statistics and Insights for %s %s's " \
                                     "Quest." % (serializer_data['first_name'],
                                                 serializer_data['last_name'])
    serializer_data['keywords'] = "Statistics, Insights, Quest"
    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'insights.html', serializer_data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def moderators(request, username):
    if not request.user.username == username:
        return redirect('quest_saga', username)
    try:
        campaign = PoliticalCampaign.get(object_uuid=username)
    except (PoliticalCampaign.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    serializer_data = PoliticalCampaignSerializer(
        campaign, context={'request': request}).data

    serializer_data['description'] = "Moderation Management for %s %s's " \
                                     "Quest." % (serializer_data['first_name'],
                                                 serializer_data['last_name'])
    serializer_data['keywords'] = "Moderators, Admins, Accountants, Editors," \
                                  " Quest"
    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'moderators.html', serializer_data)
