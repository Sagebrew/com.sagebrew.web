from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from neo4j.v1 import CypherError
from neomodel import DoesNotExist, db
from sagebrew.sb_address.neo_models import Address
from sagebrew.sb_quests.neo_models import Quest
from sagebrew.sb_quests.serializers import QuestSerializer


def quest(request, username):
    try:
        quest_obj = Quest.get(owner_username=username)
    except (CypherError, IOError, Quest.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    return redirect('profile_page', pleb_username=quest_obj.owner_username)


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class QuestSettingsView(LoginRequiredMixin):
    template_name = 'manage/quest_settings.html'

    def get(self, request, username=None):
        from sagebrew.sb_missions.neo_models import Mission
        from sagebrew.sb_missions.serializers import MissionSerializer
        from sagebrew.sb_missions.utils import order_tasks
        query = 'MATCH (person:Pleb {username: "%s"})' \
            '-[r:IS_WAGING]->(quest:Quest) WITH quest ' \
            'OPTIONAL MATCH (quest)-[:EMBARKS_ON]->(missions:Mission) ' \
            'RETURN quest, missions ORDER BY missions.created DESC' % (
                request.user.username)
        try:
            res, _ = db.cypher_query(query)
            if res.one is None:
                return redirect("404_Error")
        except CypherError:
            return redirect("500_Error")
        res.one.quest.pull()
        quest_obj = Quest.inflate(res.one.quest)
        quest_ser = QuestSerializer(quest_obj,
                                    context={'request': request}).data
        quest_ser['account_type'] = quest_obj.account_type
        if res.one.missions is None:
            mission_link = reverse('select_mission')
            mission_active = False
            onboarding_sort = []
            mission_obj = None
            onboarding_done = 0
        else:
            mission_obj = Mission.inflate(res[0].missions)
            mission_link = reverse(
                'mission_settings',
                kwargs={"object_uuid": mission_obj.object_uuid,
                        "slug": slugify(mission_obj.get_mission_title())})
            mission_active = mission_obj.active
            onboarding_sort, completed_count = order_tasks(
                mission_obj.object_uuid)
            onboarding_done = int((float(completed_count) /
                                   float(len(onboarding_sort))) * 100)
        res, _ = db.cypher_query('MATCH (a:Quest {owner_username: "%s"})'
                                 '-[:LOCATED_AT]->(b:Address) '
                                 'RETURN b' % quest_obj.owner_username)
        if res.one is not None:
            address = Address.inflate(res.one)
        else:
            address = None
        if self.template_name == "manage/quest_banking.html" \
                and address is None:
            return redirect('account_setup')
        if self.template_name == "manage/quest_settings.html":
            return redirect('general_settings')
        return render(request, self.template_name, {
            "quest": quest_ser, "mission_link": mission_link,
            "mission_active": mission_active,
            "mission": MissionSerializer(
                mission_obj, context={"request": request}).data,
            "address": address,
            "onboarding_top_3": onboarding_sort[:3],
            "onboarding_rest": onboarding_sort[3:],
            "onboarding_done": onboarding_done})
