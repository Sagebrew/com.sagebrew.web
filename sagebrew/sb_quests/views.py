from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test

from neomodel import DoesNotExist, CypherException, db

from sb_registration.utils import (verify_completed_registration)

from api.utils import smart_truncate
from sb_quests.neo_models import PoliticalCampaign, Campaign
from sb_quests.serializers import PoliticalCampaignSerializer, CampaignSerializer


from py2neo.cypher import ClientError


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


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def manage_settings(request, username):
    """
    This view provides the necessary information for rendering a user's
    Quest settings. If they have an ongoing Quest it provides the information
    for that and if not it returns nothing and the template is expected to
    provide a button for the user to start their Quest.

    :param request:
    :return:
    """
    query = 'MATCH (person:Pleb {username: "%s"})' \
            '-[r:IS_WAGING]->(campaign:Campaign) RETURN campaign' % (
                request.user.username)
    try:
        res, col = db.cypher_query(query)
        campaign = CampaignSerializer(Campaign.inflate(res[0][0]),
                                      context={'request': request}).data
        campaign['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    except(CypherException, ClientError):
        return redirect("500_Error")
    except IndexError:
        campaign = False
    return render(request, 'manage/quest_settings.html',
                  {"campaign": campaign})
