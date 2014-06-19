import httplib2
import os
import logging
import oauth2

from sagebrew.settings import base
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from .forms import (InterestForm, ProfileInfoForm, AddressInfoForm,
                    FriendInviteGmail, FriendInviteOutlook,
                    FriendInviteTwitter, FriendInviteYahoo,
                    ProfilePictureForm)

from sb_registration.models import CredentialsModel, Client_Twitter
from .utils import (generate_interests_tuple, validate_address,
                    get_google_contact_emails)
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'client_secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/contacts.readonly',
    redirect_uri='http://192.168.56.101/registration/oauth2callback/')

@login_required
def profile_information(request):
    '''
    Creates both a ProfileInfoForm and AddressInfoForm which populates the
    fields with what the user enters. If this function gets a valid POST request it
    will update the pleb. It then validates the address, through smartystreets api,
    if the address is valid a Address neo_model is created and populated.
    '''
    print request.POST
    profile_information_form = ProfileInfoForm(request.POST or None)
    address_information_form = AddressInfoForm(request.POST or None)
    try:
        citizen = Pleb.index.get(email=request.user.email)
    except Pleb.DoesNotExist:
        redirect("404_Error")
    if profile_information_form.is_valid():
        print profile_information_form.cleaned_data
        #my_pleb = Pleb(**profile_information_form.cleaned_data)
        #my_pleb.save()

    if address_information_form.is_valid():
        print address_information_form.cleaned_data
        if validate_address(address_information_form.cleaned_data):
            my_address = Address(**address_information_form.cleaned_data)
            my_address.save()
            return redirect('interests')
        else:
            print "Invalid Address"


    return render(request, 'profile_info.html',
                    {'profile_information_form':profile_information_form,
                    'address_information_form':address_information_form})


def interests(request):
    '''
    The interests view creates an InterestForm populates the topics that
    a user can choose from and if a POST request is passed then the function
    checks the validity of the arguments POSTed. If the form is valid then
    the given topics and categories are associated with the logged in user.

    :param request:
    :return: HttpResponse
    '''
    interest_form = InterestForm(request.POST or None)
    choices_tuple = generate_interests_tuple()
    interest_form.fields["specific_interests"].choices = choices_tuple

    if interest_form.is_valid():
        for item in interest_form.cleaned_data:
            if(interest_form.cleaned_data[item] and
                    item != "specific_interests"):
                try:
                    citizen = Pleb.index.get(email=request.user.email)
                except Pleb.DoesNotExist:
                    redirect("404_Error")
                try:
                    category_object = TopicCategory.index.get(
                        title=item.capitalize())
                    for topic in category_object.sb_topics.all():
                        #citizen.sb_topics.connect(topic)
                        pass
                    # citizen.topic_category.connect(category_object)
                except TopicCategory.DoesNotExist:
                    redirect("404_Error")

        for topic in interest_form.cleaned_data["specific_interests"]:
            try:
                interest_object = SBTopic.index.get(title=topic)
            except SBTopic.DoesNotExist:
                redirect("404_Error")
            # citizen.sb_topics.connect(interest_object)
        return redirect('invite_friends')

    return render(request, 'interests.html', {'interest_form': interest_form})


def invite_friends(request):
    google_friends_form = FriendInviteGmail(request.POST or None)
    outlook_friends_form = FriendInviteOutlook(request.POST or None)
    yahoo_friends_form = FriendInviteYahoo(request.POST or None)
    twitter_friends_form = FriendInviteTwitter(request.POST or None)

    twitter_consumer_key = base.TWITTER_CONSUMER_KEY
    twitter_consumer_secret = base.TWITTER_CONSUMER_SECRET

    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url = 'http://twitter.com/oauth/access_token'
    authorize_url = 'http://twitter.com/oauth/authorize'
    #get_google_contact_emails()

    '''storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build('contacts', 'v3', http=http)
        activities = service.activities()
        activitylist = activities.list(collection='public',userId='me').execute()
    logging.info(activitylist)'''


    return render(request, 'invite_friends.html', {'google_friends_form': google_friends_form,
                                                   'outlook_friends_form': outlook_friends_form,
                                                   'yahoo_friends_form': yahoo_friends_form,
                                                   'twitter_friends_form': twitter_friends_form})
                                                   #'activitylist': activitylist})

def profile_picture(request):
    profile_picture_form = ProfilePictureForm(request.POST or None)

    return render(request, 'profile_picture.html', {'profile_picture_form': profile_picture_form})



@login_required
def index(request):
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
    authorize_url = FLOW.step1_get_authorize_url()
    return HttpResponseRedirect(authorize_url)
  else:
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build('contacts', 'v3', http=http)
    activities = service.activities()
    activitylist = activities.list(collection='public',
                                   userId='me').execute()
    logging.info(activitylist)

    return render_to_response('invite_friends.html', {
                'activitylist': activitylist,
                })

@login_required
def auth_return(request):
  if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'],
                                 request.user):
    return  HttpResponseBadRequest()
  credential = FLOW.step2_exchange(request.REQUEST)
  storage = Storage(CredentialsModel, 'id', request.user, 'credential')
  storage.put(credential)
  return HttpResponseRedirect("/")