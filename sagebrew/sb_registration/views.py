from logging import getLogger

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from neomodel import (CypherException, db, DoesNotExist)

from sb_base.serializers import IntercomEventSerializer
from plebs.neo_models import Pleb
from plebs.serializers import EmailAuthTokenGenerator
from .forms import LoginForm

logger = getLogger('loggly_logs')


def advocacy(request):
    if request.user.is_authenticated() is True:
        return redirect('signup')
    return render(request, 'advocacy.html')


def political_campaign(request):
    if request.user.is_authenticated() is True:
        return redirect('signup')
    try:
        query = 'MATCH (position:Position) RETURN COUNT(position)'
        res, _ = db.cypher_query(query)
        position_count = res.one
        if position_count is None:  # pragma: no cover
            position_count = 7274
    except (CypherException, IOError):  # pragma: no cover
        position_count = 7274
    return render(request, 'political_campaign.html',
                  {"position_count": position_count})


def signup_view(request):
    if request.user.is_authenticated() is True:
        try:
            user_profile = Pleb.get(username=request.user.username,
                                    cache_buster=True)
        except DoesNotExist:
            return redirect('404_Error')
        if not user_profile.email_verified:
            return redirect('confirm_view')
        return redirect('newsfeed')
    return render(request, 'index.html')


def quest_signup(request):
    return redirect('political')


def login_view(request):
    try:
        if request.user.is_authenticated() is True:
            return redirect('newsfeed')
    except AttributeError:
        pass
    return render(request, 'login.html')


@api_view(['POST'])
def login_view_api(request):
    try:
        login_form = LoginForm(request.data)
        valid_form = login_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form is True:
        try:
            user = User.objects.get(email=login_form.cleaned_data['email'])
        except User.DoesNotExist:
            return Response({'detail': 'Incorrect password and '
                                       'username combination.'},
                            status=400)
        except MultipleObjectsReturned:  # pragma: no cover
            logger.exception("Multiple Objects Returned: ")
            return Response({'detail': 'Appears we have two users with '
                                       'that email. Please contact '
                                       'support@sagebrew.com.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user = authenticate(username=user.username,
                            password=login_form.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                rev = reverse('newsfeed')
                return Response({'detail': 'success',
                                 'user': user.email,
                                 'url': rev}, status=200)
            else:
                return Response({'detail': 'This account has been disabled.'},
                                status=400)
        else:
            return Response({'detail': 'Incorrect password and '
                                       'username combination.'}, status=400)
    else:
        return Response({'detail': 'Incorrect password and '
                                   'username combination.'}, status=400)


@login_required()
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required()
def email_verification(request, confirmation):
    from sb_quests.serializers import QuestSerializer
    try:
        try:
            profile = Pleb.get(username=request.user.username,
                               cache_buster=True)
        except DoesNotExist:
            return redirect('logout')
        token_gen = EmailAuthTokenGenerator()
        if token_gen.check_token(request.user, confirmation, profile):
            profile.email_verified = True
            profile.save()
            cache.delete(profile.username)
            serializer = IntercomEventSerializer(data={
                "event_name": "completed-email-verification",
                "username": profile.username
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if profile.mission_signup is not None:
                if profile.get_quest() is not None:
                    return redirect(profile.mission_signup)
                else:
                    serializer = QuestSerializer(
                        data={}, context={"request": request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                return redirect(profile.mission_signup)
            return redirect('newsfeed')
        else:
            return redirect('401_Error')
    except(CypherException, IOError):    # pragma: no cover
        return redirect('500_Error')
