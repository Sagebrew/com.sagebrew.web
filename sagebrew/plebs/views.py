from uuid import uuid1

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status
from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task, execute_cypher_query
from plebs.neo_models import Pleb, BetaUser, FriendRequest
from sb_registration.utils import (verify_completed_registration)
from .utils import prepare_user_search_html
from .tasks import create_friend_request_task
from .forms import (GetUserSearchForm, SubmitFriendRequestForm,
                    RespondFriendRequestForm, GetFriendRequestForm)
from .serializers import BetaUserSerializer, AddressSerializer


def root_profile_page(request):
    if request.user.is_authenticated() is True:
        return redirect("profile_page", pleb_username=request.user.username)
    else:
        return redirect("signup")


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def profile_page(request, pleb_username=""):
    """
    Displays the users profile_page. This is where we call the functions to
    determine
    who the senators are for the plebs state and which representative for
    the plebs
    district. Checks to see if the user currently accessing the page is the
    same user
    as the one who owns the page. if so it loads the page fully, if the user
    is a firend
    of the owner of the page then it allows them to see posts and comments
    on posts on the
    owners wall. If the user is neither the owner nor a friend then it only
    shows the users
    name, congressmen, reputation and profile pictures along with a button
    that allows
    them to send a friend request.

    :param request:
    :return:
    """
    try:
        citizen = Pleb.nodes.get(username=request.user.username)
        page_user_pleb = Pleb.nodes.get(username=pleb_username)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect('404_Error')
    except(CypherException):
        return HttpResponse('Server Error', status=500)
    current_user = request.user
    page_user = User.objects.get(email=page_user_pleb.email)
    is_owner = False
    is_friend = False
    friend_request_sent = False
    if current_user.email == page_user.email:
        is_owner = True
    elif page_user_pleb in citizen.friends.all():
        is_friend = True
    if page_user_pleb.username in citizen.get_friend_requests_sent():
        friend_request_sent = True

    return render(request, 'sb_plebs_base/profile_page.html', {
        'user_profile': citizen,
        'page_profile': page_user_pleb,
        'current_user': current_user,
        'page_user': page_user,
        'house_reps': [],  # reps['house_rep'],
        'senators': [],  # reps['senators'],
        'is_owner': is_owner,
        'is_friend': is_friend,
        'friend_request_sent': friend_request_sent
    })


@login_required()
def friend_page(request, pleb_username):
    try:
        citizen = Pleb.nodes.get(username=request.user.username)
        page_user_pleb = Pleb.nodes.get(username=pleb_username)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect('404_Error')
    except(CypherException):
        return HttpResponse('Server Error', status=500)
    current_user = request.user
    page_user = User.objects.get(email=page_user_pleb.email)
    is_owner = False
    is_friend = False
    friend_request_sent = False
    if current_user.email == page_user.email:
        is_owner = True
    elif page_user_pleb in citizen.friends.all():
        is_friend = True
    if page_user_pleb.username in citizen.get_friend_requests_sent():
        friend_request_sent = True
    return render(
        request, 'sb_friends_section/sb_friends.html',
        {
            'user_profile': citizen,
            'page_profile': page_user_pleb,
            'current_user': current_user,
            'page_user': page_user,
            'house_reps': [],  # reps['house_rep'],
            'senators': [],  # reps['senators'],
            'is_owner': is_owner,
            'is_friend': is_friend,
            'friend_request_sent': friend_request_sent
        })


@login_required()
def general_settings(request):
    """
    Displays the users profile_page. This is where we call the functions to
    determine
    who the senators are for the plebs state and which representative for
    the plebs
    district. Checks to see if the user currently accessing the page is the
    same user
    as the one who owns the page. if so it loads the page fully, if the user
    is a friend
    of the owner of the page then it allows them to see posts and comments
    on posts on the
    owners wall. If the user is neither the owner nor a friend then it only
    shows the users
    name, congressmen, reputation and profile pictures along with a button
    that allows
    them to send a friend request.

    :param request:
    :return:
    """
    try:
        pleb = Pleb.nodes.get(username=request.user.username)
    except (DoesNotExist, Pleb.DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError):
        return redirect("500_Error")
    address_key = settings.ADDRESS_AUTH_ID
    try:
        address = pleb.address.all()[0]
        address = AddressSerializer(address, context={'request': request}).data
    except IndexError:
        address = False
    return render(request, 'general_settings.html',
                  {"address": address, "address_key": address_key})


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
        response = prepare_user_search_html(pleb=form.cleaned_data['username'])
        if response is None:
            return HttpResponse('Server Error', status=500)
        elif response is False:
            return HttpResponse('Bad Email', status=400)
        return Response({'html': response}, status=200)
    else:
        return Response({'detail': 'error'}, 400)


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
    except (BetaUser.DoesNotExist, DoesNotExist) as e:
        return Response({"detail": e.message}, status=status.HTTP_404_NOT_FOUND)
    except (IOError, CypherException) as e:
        return Response({"detail": e.message},
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_friend_requests(request):
    """
    gets all friend requests attached to the user and returns
    a list of dictionaries of requests

    :param request:
    :return:
    """
    requests = []
    try:
        form = GetFriendRequestForm(request.DATA)
        valid_form = form.is_valid()
    except AttributeError:
        return Response({'detail': 'attribute error'}, status=400)

    if valid_form is True:
        query = 'match (p:Pleb) where p.email ="%s" ' \
                'with p ' \
                'match (p)-[:RECEIVED_A_REQUEST]-(r:FriendRequest) ' \
                'where r.seen=False ' \
                'return r' % request.DATA['email']
        friend_requests, meta = execute_cypher_query(query)
        friend_requests = [FriendRequest.inflate(row[0])
                           for row in friend_requests]
        for friend_request in friend_requests:
            request_id = friend_request.object_uuid
            request_dict = {
                'from_name': request.user.get_full_name(),
                'from_email': request.user.email,
                'request_id': request_id}
            requests.append(request_dict)
        return Response(requests, status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def respond_friend_request(request):
    """
    finds the friend request which is attached to both the from and to user
    then, depending on the response type, either attaches the friend
    relationship
    in each pleb and deletes the request, deletes the request, or lets the
    friend
    request exist to stop the user from sending more but does not notify the
    user
    which blocked them that they have a friend request from them.

    :param request:
    :return:
    """
    try:
        form = RespondFriendRequestForm(request.DATA)
        valid_form = form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form is True:
        try:
            friend_request = FriendRequest.nodes.get(
                object_uuid=form.cleaned_data['request_id'])
            to_pleb = friend_request.request_to.all()[0]
            from_pleb = friend_request.request_from.all()[0]
        except (FriendRequest.DoesNotExist, Pleb.DoesNotExist, IndexError):
            # TODO should we be doing something different for an index error?
            return Response(status=404)
        except (CypherException, IOError):
            return Response(status=500)

        if form.cleaned_data['response'] == 'accept':
            rel1 = to_pleb.friends.connect(from_pleb)
            rel2 = from_pleb.friends.connect(to_pleb)
            rel1.save()
            rel2.save()
            friend_request.delete()
            to_pleb.save()
            from_pleb.save()
            return Response(status=200)
        elif form.cleaned_data['response'] == 'deny':
            friend_request.delete()
            return Response(status=200)
        elif form.cleaned_data['response'] == 'block':
            friend_request.seen = True
            friend_request.response = 'block'
            friend_request.save()
            return Response(status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)


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
