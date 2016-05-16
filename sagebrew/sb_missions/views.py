from django.utils.text import slugify
from django.views.generic import View
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from py2neo.cypher.error import ClientError
from neomodel import db, CypherException, DoesNotExist

from sb_updates.neo_models import Update
from sb_updates.serializers import UpdateSerializer
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_missions.utils import order_tasks
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


def mission_redirect_page(request, object_uuid=None):
    try:
        mission_obj = Mission.get(object_uuid)
    except (Mission.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, ClientError, IOError):
        return redirect("500_Error")

    return redirect("mission", object_uuid=object_uuid,
                    slug=slugify(mission_obj.get_mission_title()),
                    permanent=True)


def mission_edit_updates(request, object_uuid, slug=None, edit_id=None):
    query = 'MATCH (update:Update {object_uuid: "%s"})-[:ABOUT]->' \
            '(mission:Mission)<-[:EMBARKS_ON]-(quest:Quest)' \
            'WITH update, mission, quest ' \
            'MATCH (quest)-[:EMBARKS_ON]->(missions:Mission) ' \
            'RETURN mission, quest, update, missions ' \
            'ORDER BY missions.created DESC' % edit_id
    res, _ = db.cypher_query(query)
    if res.one is None:
        return redirect("select_mission")

    missions = [MissionSerializer(Mission.inflate(row.missions)).data
                for row in res]
    mission_obj = Mission.inflate(res.one.mission)
    return render(
        request, 'manage/edit_update.html', {
            "update": UpdateSerializer(
                Update.inflate(res.one.update)).data,
            "mission": MissionSerializer(mission_obj).data,
            "slug": slugify(mission_obj.get_mission_title()),
            "quest": QuestSerializer(Quest.inflate(res.one.quest)).data,
            "missions": missions
        })


def mission_updates(request, object_uuid, slug=None):
    # Only need to check that at least one update exists here to mark that
    # updates are available for this mission.
    query = 'MATCH (quest:Quest)-[:EMBARKS_ON]->' \
            '(mission:Mission {object_uuid: "%s"}) ' \
            'WITH quest, mission ' \
            'OPTIONAL MATCH (mission)<-[:ABOUT]-(updates:Update) ' \
            'RETURN quest, mission, ' \
            'CASE WHEN count(updates) > 0 ' \
            'THEN true ELSE false END AS update' % object_uuid
    res, _ = db.cypher_query(query)
    if res.one is None:
        return redirect("404_Error")
    # Instead of doing inflation and serialization of all the updates here
    # without pagination lets just indicate if we have any or not and then
    # hit the endpoint to gather the actual updates.
    quest = Quest.inflate(res.one.quest)
    mission_obj = Mission.inflate(res.one.mission)
    return render(request, 'mission/updates.html', {
        "updates": res.one.update,
        "mission": MissionSerializer(mission_obj).data,
        "slug": slugify(mission_obj.get_mission_title()),
        "quest": QuestSerializer(quest).data
    })


def mission_endorsements(request, object_uuid, slug=None):
    # Just check if there are any endorsements either from a Pleb or a Quest
    query = 'MATCH (quest:Quest)-[:EMBARKS_ON]->' \
            '(mission:Mission {object_uuid:"%s"}) ' \
            'WITH quest, mission ' \
            'OPTIONAL MATCH (mission)<-[:ENDORSES]-(endorsement) ' \
            'RETURN endorsement, quest, mission' % object_uuid
    res, _ = db.cypher_query(query)
    # Instead of doing inflation and serialization of all the updates here
    # without pagination lets just indicate if we have any or not and then
    # hit the endpoint to gather the actual updates.
    quest = Quest.inflate(res.one.quest)
    mission_obj = Mission.inflate(res.one.mission)
    return render(request, 'mission/endorsements.html', {
        "quest": QuestSerializer(quest).data,
        "mission": MissionSerializer(mission_obj).data,
        "slug": slugify(mission_obj.get_mission_title()),
        "endorsements":
            True if res.one.endorsement else False
    })


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class MissionSettingsView(LoginRequiredMixin):
    template_name = 'manage/mission_settings.html'

    def get(self, request, object_uuid=None, slug=None):
        # Do a second optional match to get the list of missions,
        # the first is just to make sure we're dealing with the actual
        # owner of the Mission.
        query = 'MATCH (pleb:Pleb {username: "%s"})-[:IS_WAGING]->' \
            '(quest:Quest) WITH quest ' \
            'OPTIONAL MATCH (quest)-[:EMBARKS_ON]->(missions:Mission) ' \
            'RETURN missions, quest ' \
            'ORDER BY missions.created DESC' % request.user.username
        res, _ = db.cypher_query(query)
        if res.one is None:
            return redirect("404_Error")
        if res.one.missions is None:
            return redirect("select_mission")
        if object_uuid is None:
            mission_obj = Mission.inflate(res[0].missions)
            return redirect('mission_settings',
                            object_uuid=mission_obj.object_uuid,
                            slug=slugify(mission_obj.get_mission_title()))

        mission_obj = Mission.get(object_uuid)
        missions = [MissionSerializer(Mission.inflate(row.missions)).data
                    for row in res]
        quest = Quest.inflate(res.one.quest)
        if mission_obj.owner_username != quest.owner_username:
            return redirect("404_Error")
        onboarding_sort, completed_count = order_tasks(object_uuid)
        if len(onboarding_sort) != 0:
            onboarding_done = int((float(completed_count) /
                                   float(len(onboarding_sort))) * 100)
        else:
            onboarding_done = 0
        return render(request, self.template_name, {
            "missions": missions,
            "mission": MissionSerializer(mission_obj,
                                         context={"request": request}).data,
            "quest": QuestSerializer(quest, context={"request": request}).data,
            "slug": slugify(mission_obj.get_mission_title()),
            "epic_template": render_to_string("placeholder_epic.html"),
            "update_placeholder": render_to_string("updates/placeholder.html"),
            "onboarding_top_3": onboarding_sort[:3],
            "onboarding_rest": onboarding_sort[3:],
            "onboarding_done": onboarding_done
        })


class MissionBaseView(View):
    template_name = 'mission/mission.html'

    def get(self, request, object_uuid=None, slug=None):
        try:
            mission_obj = Mission.get(object_uuid)
        except (Mission.DoesNotExist, DoesNotExist):
            return redirect("404_Error")
        except (CypherException, ClientError, IOError):
            return redirect("500_Error")
        mission_dict = MissionSerializer(
            mission_obj, context={'request': request}).data
        mission_dict['slug'] = slugify(mission_obj.get_mission_title())

        return render(request, self.template_name, {
            "mission": mission_dict,
            "quest": QuestSerializer(
                Quest.get(mission_obj.owner_username)).data
        })
