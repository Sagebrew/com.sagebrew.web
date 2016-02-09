from django.views.generic import View
from django.utils.text import slugify
from django.core.urlresolvers import reverse

from django.shortcuts import redirect, render

from py2neo.cypher import ClientError
from neomodel import DoesNotExist, CypherException, db

from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


class ContributionMissionView(View):
    """
    Single mission donation. See Quest Donation for managing a list of missions
    that the user can use a drop down for.
    """
    template_name = 'volunteer/volunteer.html'

    def get(self, request, object_uuid=None, slug=None):
        try:
            mission = Mission.get(object_uuid)
        except (Mission.DoesNotExist, DoesNotExist):
            return redirect("404_Error")
        except (CypherException, ClientError, IOError):
            return redirect("500_Error")
        quest = Quest.get(mission.owner_username)
        reverse_params = {"object_uuid": object_uuid, "slug": slug}
        if "volunteer/option" in request.path and \
                not request.user.is_authenticated():
            return redirect("mission_volunteer_name", **reverse_params)
        elif request.path == \
                reverse("mission_volunteer_name", kwargs=reverse_params) and \
                request.user.is_authenticated():
            return redirect("mission_volunteer_option", **reverse_params)
        elif request.path == request.path == \
                reverse("mission_donation_name", kwargs=reverse_params) and \
                request.user.is_authenticated():
            return redirect("mission_donation_amount", **reverse_params)
        elif request.path == request.path == \
                reverse("mission_donation_payment", kwargs=reverse_params) and \
                not request.user.is_authenticated():
            return redirect("mission_donation_amount", **reverse_params)
        return render(request, self.template_name, {
            "selected": MissionSerializer(mission).data,
            "quest": QuestSerializer(quest).data,
            "slug": slugify(mission.get_mission_title()),
            "missions": None
        })


class ContributionQuestView(View):
    """
    Single mission donation. See Quest Donation for managing a list of missions
    that the user can use a drop down for.
    """
    template_name = 'volunteer/volunteer.html'

    def get(self, request, username=None):
        try:
            quest = Quest.get(username)
        except (Quest.DoesNotExist, DoesNotExist):
            return redirect("404_Error")
        except (CypherException, ClientError, IOError):
            return redirect("500_Error")
        query = 'MATCH (quest:Quest {object_uuid: "%s"})-[:EMBARKS_ON]->' \
                '(missions:Mission) RETURN missions, quest ' \
                'ORDER BY missions.created DESC' % quest.object_uuid
        res, _ = db.cypher_query(query)
        if res.one is None:
            missions = None
        else:
            missions = [MissionSerializer(Mission.inflate(row.missions)).data
                        for row in res]
        return render(request, self.template_name, {
            "selected": QuestSerializer(quest).data,
            "quest": QuestSerializer(quest).data,
            "slug": None,
            "missions": missions,
        })
