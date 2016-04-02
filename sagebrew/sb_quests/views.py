from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from py2neo.cypher import ClientError
from neomodel import DoesNotExist, CypherException, db

from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


def quest(request, username):
    try:
        quest_obj = Quest.get(owner_username=username)
    except (CypherException, IOError, Quest.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    serializer_data = {
        "quest": QuestSerializer(quest_obj, context={'request': request}).data,
        "keywords": "Politics, Fundraising, Campaign, Quest, Activism"
    }
    if serializer_data['quest']['about'] is not None:
        serializer_data['description'] = serializer_data['quest']['about']
    else:
        serializer_data['description'] = "%s %s's Policies, Agenda, " \
                                         "and Platform." % (
                                             serializer_data['quest'][
                                                 'first_name'],
                                             serializer_data['quest'][
                                                 'last_name'])
    return render(request, 'quest.html', serializer_data)


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class QuestSettingsView(LoginRequiredMixin):
    template_name = 'manage/quest_settings.html'

    def get(self, request, username=None):
        query = 'MATCH (person:Pleb {username: "%s"})' \
            '-[r:IS_WAGING]->(quest:Quest) RETURN quest' % (
                request.user.username)
        try:
            res, _ = db.cypher_query(query)
            if res.one is None:
                return redirect("404_Error")
        except(CypherException, ClientError):
            return redirect("500_Error")
        res.one.pull()
        quest_obj = Quest.inflate(res.one)
        quest_ser = QuestSerializer(quest_obj,
                                    context={'request': request}).data
        quest_ser['account_type'] = quest_obj.account_type
        return render(request, self.template_name, {"quest": quest_ser})
