from django.views.generic import View
from django.utils.text import slugify

from django.shortcuts import redirect, render

from py2neo.cypher import ClientError
from neomodel import DoesNotExist, CypherException, db

from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


class DonationMissionView(View):
    """
    Single mission donation. See Quest Donation for managing a list of missions
    that the user can use a drop down for.
    """
    template_name = 'donations/amount.html'

    def get(self, request, object_uuid=None, slug=None):
        try:
            mission = Mission.get(object_uuid)
        except (Mission.DoesNotExist, DoesNotExist):
            return redirect("404_Error")
        except (CypherException, ClientError, IOError):
            return redirect("500_Error")
        quest = Quest.get(mission.owner_username)
        return render(request, self.template_name, {
            "selected": MissionSerializer(mission).data,
            "quest": QuestSerializer(quest).data,
            "slug": slugify(mission.get_mission_title()),
            "missions": None
        })


class DonationQuestView(View):
    """
    Single mission donation. See Quest Donation for managing a list of missions
    that the user can use a drop down for.
    """
    template_name = 'donations/amount.html'

    def get(self, request, username=None, slug=None):
        try:
            quest = Quest.get(username)
        except (Quest.DoesNotExist, DoesNotExist):
            return redirect("404_Error")
        except (CypherException, ClientError, IOError):
            return redirect("500_Error")
        query = 'MATCH (quest:Quest {object_uuid: "%s"})-[:EMBARKS_ON]->' \
                '(missions:Mission) RETURN missions, quest' \
                'ORDER BY missions.created DESC' % quest.object_uuid
        res, _ = db.cypher_query(query)
        if res.one is None:
            # TODO redirect to mission list page instead of 404
            return redirect("404_Error")
        missions = [MissionSerializer(Mission.inflate(row.missions)).data
                    for row in res]
        return render(request, self.template_name, {
            "selected": None,
            "quest": quest,
            "slug": None,
            "missions": missions,
        })
