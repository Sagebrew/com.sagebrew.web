from django.views.generic import View
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from py2neo.cypher import ClientError
from neomodel import DoesNotExist, CypherException, db

from api.utils import spawn_task
from plebs.tasks import send_email_task
from sb_registration.utils import (verify_completed_registration)
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


def quest(request, username):
    try:
        quest_obj = Quest.get(owner_username=username)
    except (CypherException, IOError, Quest.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    serializer_data = {
        "quest": QuestSerializer(quest_obj, context={'request': request}).data,
        "stripe_key": settings.STRIPE_PUBLIC_KEY,
        "keywords": "Politics, Fundraising, Campaign, Quest, Activism"
    }
    # TODO think we can remove this and just use the stripe key coming through
    # the context processor
    if serializer_data['quest']['about'] is not None:
        serializer_data['description'] = serializer_data['about']
    else:
        serializer_data['description'] = "%s %s's Policies, Agenda, " \
                                         "and Platform." % (
                                             serializer_data['quest'][
                                                 'first_name'],
                                             serializer_data['quest'][
                                                 'last_name'])
    return render(request, 'quest.html', serializer_data)


def quest_list(request):
    serializer_data = []
    return render(request, 'quest_list.html', serializer_data)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def insights(request, username):
    if request.user.username not in Quest.get_quest_helpers(username):
        return redirect('quest', username)
    try:
        quest_obj = Quest.get(username)
    except (Quest.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    serializer_data = QuestSerializer(quest_obj,
                                      context={'request': request}).data
    serializer_data['description'] = "Statistics and Insights for %s %s's " \
                                     "Quest." % (serializer_data['first_name'],
                                                 serializer_data['last_name'])
    serializer_data['keywords'] = "Statistics, Insights, Quest"
    serializer_data['stripe_key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'insights.html', serializer_data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_quest(request):
    internal_data = {
        "source": "support@sagebrew.com",
        "to": [row[1] for row in settings.ADMINS],
        "subject": "Quest Deletion",
        "html_content": render_to_string(
            "email_templates/email_internal_quest_deletion.html", {
                "username": request.user.username,
                "email": request.user.email
            })
    }
    user_data = {
        "source": "support@sagebrew.com",
        "to": request.user.email,
        "subject": "Quest Deletion Confirmation",
        "html_content": render_to_string(
            "email_templates/email_quest_deletion_confirmation.html", {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name
            })
    }
    spawn_task(task_func=send_email_task, task_param=internal_data)
    spawn_task(task_func=send_email_task, task_param=user_data)
    return Response({"detail": "We have sent a confirmation email to you "
                               "and will be in contact soon to follow up!"},
                    status=status.HTTP_200_OK)


class LoginRequiredMixin(View):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class QuestSettingsView(LoginRequiredMixin):
    template_name = 'manage/quest_settings.html'

    @method_decorator(user_passes_test(
        verify_completed_registration,
        login_url='/registration/profile_information'))
    def dispatch(self, *args, **kwargs):
        return super(QuestSettingsView, self).dispatch(*args, **kwargs)

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
        quest_obj = QuestSerializer(Quest.inflate(res.one),
                                    context={'request': request}).data
        return render(request, self.template_name, {"quest": quest_obj})
