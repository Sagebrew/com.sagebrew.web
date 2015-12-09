from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test

from neomodel import DoesNotExist, CypherException

from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer

from sb_registration.utils import verify_completed_registration

from .neo_models import Update
from .serializers import UpdateSerializer


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def edit_update(request, object_uuid=None, username=None):
    try:
        update = Update.nodes.get(object_uuid=object_uuid)
    except (Update.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    return render(request, 'create_update.html', UpdateSerializer(update).data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def create_update(request, username):
    try:
        quest = Quest.get(owner_username=username)
    except (Quest.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    return render(request, 'create_update.html',
                  QuestSerializer(quest, context={'request': request}).data)


def updates(request, username):
    try:
        quest = Quest.get(owner_username=username)
    except (Quest.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    serializer_data = QuestSerializer(
        quest, context={'request': request}).data
    serializer_data['description'] = "Updates for %s %s's Quest" % (
        serializer_data['first_name'], serializer_data['last_name'])
    serializer_data['keywords'] = "Updates, Events, Fundraising, Volunteer, " \
                                  "Politics, Campaign, Quest, " \
                                  "Candidate, Representative"
    if serializer_data.get('seat_formal_name'):
        serializer_data['keywords'] += ", %s" % serializer_data.get(
            'seat_formal_name', "")
    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'updates.html', serializer_data)
