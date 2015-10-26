from uuid import uuid1

from django.template.loader import render_to_string
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.conf import settings
from django.views.generic import View
from django.template import RequestContext

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status

from py2neo.cypher import ClientError

from neomodel import DoesNotExist, CypherException, db

from api.utils import spawn_task
from plebs.neo_models import (Pleb, BetaUser, Address,
                              get_friend_requests_sent)
from sb_registration.utils import (verify_completed_registration)
from sb_quests.neo_models import Campaign
from sb_quests.serializers import CampaignSerializer

from .serializers import PlebSerializerNeo
from .tasks import create_friend_request_task, send_email_task
from .forms import (GetUserSearchForm, SubmitFriendRequestForm)
from .serializers import BetaUserSerializer, AddressSerializer


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


class ProfileView(LoginRequiredMixin):
    template_name = 'sb_plebs_base/profile_page.html'

    @method_decorator(user_passes_test(
        verify_completed_registration,
        login_url='/registration/profile_information'))
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)

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
        is_owner = False
        query = 'MATCH (person:Pleb {username: "%s"})' \
                '-[r:FRIENDS_WITH]->(p:Pleb {username: "%s"}) ' \
                'RETURN CASE WHEN r.currently_friends = True THEN True ' \
                'WHEN r.currently_friends = False THEN False ' \
                'ELSE False END AS result' % (request.user.username,
                                              page_user.username)
        try:
            res, col = db.cypher_query(query)
            are_friends = bool(res[0])
        except(CypherException, ClientError):
            return redirect("500_Error")
        except IndexError:
            is_owner = True
            are_friends = False
        return render(request, self.template_name, {
            'page_profile': PlebSerializerNeo(
                page_user_pleb,
                context={'expand': True, 'request': request}).data,
            'page_user': page_user,
            'is_owner': is_owner,
            'is_friend': are_friends,
            'friend_request_sent': get_friend_requests_sent(
                request.user.username, page_user.username)
        })


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
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
    except IndexError:
        address = False
    return render(request, 'general_settings.html',
                  {"address": address, "address_key": address_key})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def quest_settings(request):
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
    return render(request, 'quest_settings.html',
                  {"campaign": campaign})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def contribute_settings(request):
    """
    This view provides the necessary information for rendering a user's
    Quest settings. If they have an ongoing Quest it provides the information
    for that and if not it returns nothing and the template is expected to
    provide a button for the user to start their Quest.

    :param request:
    :return:
    """
    return render(request, 'contribute_settings.html',
                  {"stripe_key": settings.STRIPE_PUBLIC_KEY})


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_user_search_view(request, pleb_username=""):
    """
    This view will take a plebs email, get the user and render to string
    an html object which holds the data to be displayed when a user is returned
    in a search.

    :param request:
    :param pleb_username:
    :return:
    """
    form = GetUserSearchForm({"username": pleb_username})
    if form.is_valid() is True:
        profile = cache.get(pleb_username)
        current_user = cache.get(request.user.username)
        if profile is None:
            try:
                profile = Pleb.nodes.get(username=pleb_username)
            except(Pleb.DoesNotExist, DoesNotExist):
                return Response({"detail": "Sorry we could not find "
                                           "that user."},
                                status=status.HTTP_404_NOT_FOUND)
            cache.set(pleb_username, profile)
        if current_user is None:
            current_user = Pleb.nodes.get(username=request.user.username)

        if profile in current_user.friends.all():
            is_friend = True
            friend_request_sent = True
        else:
            is_friend = False
            friend_request_sent = current_user.get_friend_requests_sent(
                profile.username)
        serializer_data = PlebSerializerNeo(profile).data
        serializer_data['is_friend'] = is_friend

        serializer_data['friend_request_sent'] = friend_request_sent
        context = RequestContext(request, serializer_data)
        return Response(
            {
                'html': render_to_string('user_search_block.html',
                                         context)},
            status=200)
    else:
        return Response({'detail': 'error'}, 400)


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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def authenticate_representative(request):
    pleb = Pleb.get(request.user.username)
    email_data = {
        "source": "support@sagebrew.com",
        "to": [row[1] for row in settings.ADMINS],
        "subject": "Representative Authentication",
        "html_content": render_to_string(
            "email_templates/email_internal_representative_confirmation.html",
            {"username": pleb.username, "phone": pleb.get_official_phone()})
    }
    spawn_task(task_func=send_email_task, task_param=email_data)
    return Response({"detail": "We will be call your office phone to "
                               "verify soon."},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def deactivate_user(request):
    request.user.is_active = False
    request.user.save()
    return Response({"detail": "successfully deactivated user"}, 200)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def invite_beta_user(request, email):
    try:
        beta_user = BetaUser.nodes.get(email=email)
        beta_user.invite()
    except (BetaUser.DoesNotExist, DoesNotExist):
        return Response({"detail": "Sorry we could not find that user."},
                        status=status.HTTP_404_NOT_FOUND)
    except (IOError, CypherException, ClientError):
        return Response({"detail": "Sorry looks like we're having"
                                   " some server difficulties"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"detail": None}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_friend_request(request):
    """
    calls the task which creates a friend request, it also creates the id
    for the
    request here

    :param request:
    :return:
    """
    # TODO return uuid of friend request and add to javascript hide button
    # when uuid received
    # if action is True hide friend request button and show a delete friend
    # request button
    friend_request_data = request.data
    if isinstance(friend_request_data, dict) is False:
        return Response({'detail': 'attribute error'}, status=400)
    request_form = SubmitFriendRequestForm(friend_request_data)
    # TODO Think we're moving this kind of stuff out to the JS system
    # But until then needs to come after the form since it can cause
    # Type errors if someone passes something other than a dict
    object_uuid = str(uuid1())

    if request_form.is_valid() is True:
        task_data = {
            "from_username": request.user.username,
            "to_username": request_form.cleaned_data['to_username'],
            "object_uuid": object_uuid
        }
        spawned = spawn_task(task_func=create_friend_request_task,
                             task_param=task_data)
        if isinstance(spawned, Exception) is True:
            return Response({'detail': 'server error'}, status=500)
        return Response({"action": True,
                         "friend_request_id": object_uuid}, status=200)
    else:
        return Response({'detail': 'invalid form'}, status=400)


class ListBetaUsers(ListAPIView):
    queryset = BetaUser.nodes.all()
    serializer_class = BetaUserSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)


class RetrieveBetaUsers(RetrieveAPIView):
    serializer_class = BetaUserSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)

    def retrieve(self, request, *args, **kwargs):
        queryset = BetaUser.nodes.get(email=kwargs["email"])
        serializer_class = BetaUserSerializer(queryset)
        return Response(serializer_class.data)
