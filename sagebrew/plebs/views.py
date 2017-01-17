from intercom import Message, Intercom

from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.views.generic import View

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from py2neo.cypher import ClientError

from neomodel import DoesNotExist, CypherException, db

from sb_address.neo_models import Address
from sb_address.serializers import AddressSerializer
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer

from .neo_models import Pleb
from .serializers import PlebSerializerNeo


def root_profile_page(request):
    if request.user.is_authenticated() is True:
        return redirect("newsfeed")
    else:
        return redirect("signup")


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class PersonalProfileView(LoginRequiredMixin):
    template_name = 'profile_page.html'

    def get(self, request):
        try:
            query = 'MATCH (q:Quest {owner_username:"%s"}) RETURN q' % (
                request.user.username)
            res, _ = db.cypher_query(query)
            quest = QuestSerializer(Quest.inflate(res[0][0]),
                                    context={'request': request}).data
        except (DoesNotExist, Quest.DoesNotExist):
            quest = None
        return render(request, self.template_name, {
            'page_profile': PlebSerializerNeo(
                Pleb.get(username=request.user.username),
                context={'expand': True, 'request': request}).data,
            'page_user': User.objects.get(username=request.user.username),
            'quest': quest
        })


class ProfileView(View):
    template_name = 'profile_page.html'

    def get(self, request, pleb_username=None):
        if pleb_username is None:
            pleb_username = request.user.username
        try:
            page_user_pleb = Pleb.get(username=pleb_username)
        except (Pleb.DoesNotExist, DoesNotExist):
            return redirect('404_Error')
        except (CypherException, ClientError):
            return redirect("500_Error")
        page_user = User.objects.get(username=page_user_pleb.username)
        if page_user.username == request.user.username:
            is_owner = True
        else:
            is_owner = False

        return render(request, self.template_name, {
            'page_profile': PlebSerializerNeo(
                page_user_pleb,
                context={'expand': True, 'request': request}).data,
            'page_user': page_user,
            'is_owner': is_owner
        })


@login_required()
def general_settings(request):
    """
    Displays the users profile_page. This is where we call the functions to
    determine who the senators are for the plebs state and which
    representative for the plebs district. Checks to see if the user
    currently accessing the page is the same user as the one who owns the page.
    If so it loads the page fully, if the user is a friend of the owner of the
    page then it allows them to see posts and comments on posts on the
    owners wall. If the user is neither the owner nor a friend then it only
    shows the users name, congressmen, reputation and profile pictures along
    with a button that allows them to send a friend request.

    :param request:
    :return:
    """
    address_key = settings.ADDRESS_AUTH_ID
    query = 'MATCH (person:Pleb {username: "%s"})' \
            '-[r:LIVES_AT]->(house:Address) RETURN house' % (
                request.user.username)
    try:
        res, col = db.cypher_query(query)
        address = AddressSerializer(Address.inflate(res[0][0]),
                                    context={'request': request}).data
    except(CypherException, ClientError):
        return redirect("500_Error")
    try:
        query = 'MATCH (q:Quest {owner_username:"%s"}) RETURN q' % (
            request.user.username)
        res, _ = db.cypher_query(query)
        quest = QuestSerializer(Quest.inflate(res[0][0]),
                                context={'request': request}).data
    except (DoesNotExist, Quest.DoesNotExist):
        quest = None
    except IndexError:
        address = False
    return render(request, 'settings/general_settings.html',
                  {"address": address, "address_key": address_key,
                   "quest": quest})


@login_required()
def delete_account(request):
    """
    Delete account page.
    """
    try:
        query = 'MATCH (q:Quest {owner_username:"%s"}) RETURN q' % (
            request.user.username)
        res, _ = db.cypher_query(query)
        quest = QuestSerializer(Quest.inflate(res[0][0]),
                                context={'request': request}).data
    except (DoesNotExist, Quest.DoesNotExist):
        quest = None
    return render(request, 'settings/delete_account.html', {"quest": quest})


@login_required()
def contribute_settings(request):
    """
    This view provides the necessary information for rendering a user's
    Quest settings. If they have an ongoing Quest it provides the information
    for that and if not it returns nothing and the template is expected to
    provide a button for the user to start their Quest.

    :param request:
    :return:
    """
    try:
        query = 'MATCH (q:Quest {owner_username:"%s"}) RETURN q' % (
            request.user.username)
        res, _ = db.cypher_query(query)
        quest = QuestSerializer(Quest.inflate(res[0][0]),
                                context={'request': request}).data
    except (DoesNotExist, Quest.DoesNotExist):
        quest = None
    return render(request, 'settings/contribute_settings.html',
                  {"stripe_key": settings.STRIPE_PUBLIC_KEY, "quest": quest})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def authenticate_representative(request):
    Intercom.app_id = settings.INTERCOM_APP_ID
    Intercom.app_api_key = settings.INTERCOM_API_KEY
    pleb = Pleb.get(request.user.username)
    message_data = {
        'message_type': 'email',
        'subject': "Representative Authentication",
        'body': render_to_string(
            "email_templates/internal_representative_confirmation.html",
            {"username": pleb.username, "phone": pleb.get_official_phone()}),
        'template': "personal",
        'from': {
            'type': "admin",
            'id': settings.INTERCOM_ADMIN_ID_DEVON
        },
        'to': {
            'type': "user",
            'user_id': "devon_bleibtrey"
        }
    }
    Message.create(**message_data)
    return Response({"detail": "We will be call your office phone to "
                               "verify soon."},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def deactivate_user(request):
    request.user.is_active = False
    request.user.save()
    return Response({"detail": "successfully deactivated user"}, 200)
