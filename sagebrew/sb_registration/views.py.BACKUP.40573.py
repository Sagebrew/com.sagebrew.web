import os

<<<<<<< HEAD

=======
from django.conf import settings
from uuid import uuid1
>>>>>>> fe315a231e0d30729ec78b462db22c6940e10daf
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings

from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build


from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from .forms import (InterestForm, ProfileInfoForm, AddressInfoForm,
                    FriendInviteGmail, FriendInviteOutlook,
                    FriendInviteTwitter, FriendInviteYahoo)

from .models import CredentialsModel, FlowModel
from .utils import (generate_interests_tuple, validate_address,
                    get_google_contact_emails,)

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
print CLIENT_SECRETS
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='http://www.google.com/m8/feeds/',
    redirect_uri='https://192.168.56.101/registration/oauth2callback/')
=======
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from .forms import (ProfileInfoForm, AddressInfoForm, InterestForm, ProfilePictureForm,
                    ProfilePageForm, AddressChoiceForm)
from .utils import validate_address, generate_interests_tuple, upload_image, compare_address
>>>>>>> fe315a231e0d30729ec78b462db22c6940e10daf

@login_required
def profile_information(request):
    '''
    Creates both a ProfileInfoForm and AddressInfoForm which populates the
    fields with what the user enters. If this function gets a valid POST request it
    will update the pleb. It then validates the address, through smartystreets api,
    if the address is valid a Address neo_model is created and populated.
    '''
    address_selection = False
    print request.POST
    profile_information_form = ProfileInfoForm(request.POST or None)
    address_information_form = AddressInfoForm(request.POST or None)
    address_selection_form = AddressChoiceForm(request.POST or None)
    try:
        citizen = Pleb.index.get(email=request.user.email)
    except Pleb.DoesNotExist:
        return redirect("404_Error")
    if profile_information_form.is_valid():
        print profile_information_form.cleaned_data
        #my_pleb = Pleb(**profile_information_form.cleaned_data)
        #my_pleb.save()

    if address_information_form.is_valid():
        print address_information_form.cleaned_data
        address_info = validate_address(address_information_form.cleaned_data)

        if address_info['length'] == 1:
            if compare_address():
                my_address = Address(**address_information_form.cleaned_data)
                my_address.save()
                citizen.completed_profile_info = True
                citizen.save()
                return redirect('interests')

        elif address_info['length'] > 1:
            address_selection = 'choices'
            address_selection_form.fields['address_options'].choices = ('',)
            address_selection_form.fields['address_options'].required = True

        else:
            address_selection = 'no_choices'
            print "Please enter a valid address"


    return render(request, 'profile_info.html',
                    {'profile_information_form': profile_information_form,
                    'address_information_form': address_information_form,
                    'address_selection': address_selection,
                    'address_choice_form': address_selection_form})

@login_required()
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
                    if citizen.completed_profile_info:
                        return redirect('profile_page')
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
        return redirect('profile_picture')

    return render(request, 'interests.html', {'interest_form': interest_form})

<<<<<<< HEAD
@login_required
def invite_friends(request):
    google_friends_form = FriendInviteGmail(request.POST or None)
    outlook_friends_form = FriendInviteOutlook(request.POST or None)
    yahoo_friends_form = FriendInviteYahoo(request.POST or None)
    twitter_friends_form = FriendInviteTwitter(request.POST or None)

    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        print "redirecting"
        return HttpResponseRedirect(authorize_url)
    else:
        print "Getting contacts"
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build("contacts", "v3", http=http)
        activities = service.activities()
        activitylist = activities.list(collection='public',userId='me').execute()
        logging.info(activitylist)
        return render_to_response('invite_friends.html', {
                'activitylist': activitylist,
                })
    '''
    return render(request, 'invite_friends.html', {'google_friends_form': google_friends_form,
                                                   'outlook_friends_form': outlook_friends_form,
                                                   'yahoo_friends_form': yahoo_friends_form,
                                                   'twitter_friends_form': twitter_friends_form,
                                                   'activitylist': activitylist})
    '''


@login_required
def auth_return(request):
    print request.REQUEST
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'],
                                 request.user):
        return  HttpResponseBadRequest()

    credential = FLOW.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    return HttpResponseRedirect("/")
=======

@login_required()
def profile_picture(request):
    if request.method == 'POST':
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)
        if profile_picture_form.is_valid():
            try:
                citizen = Pleb.index.get(email=request.user.email)
                if citizen.completed_profile_info:
                    return redirect('profile_page')
                print citizen.profile_pic
            except Pleb.DoesNotExist:
                print("How did you even get here!?")
                return render(request, 'profile_picture.html', {'profile_picture_form': profile_picture_form})
            image_uuid = uuid1()
            data = request.FILES['picture']
            temp_file = '%s%s.jpeg' % (settings.TEMP_FILES, image_uuid)
            with open(temp_file, 'wb+') as destination:
                for chunk in data.chunks():
                    destination.write(chunk)
            citizen.profile_pic = upload_image('profile_pictures', image_uuid)
            citizen.save()
            return redirect('profile_page')
    else:
        profile_picture_form = ProfilePictureForm()
    return render(request, 'profile_picture.html', {'profile_picture_form': profile_picture_form})

@login_required()
def profile_page(request):#who is your sen
    profile_page_form = ProfilePageForm(request.POST or None)

    return render(request, 'profile_page.html', {'profile_page_form': profile_page_form})

>>>>>>> fe315a231e0d30729ec78b462db22c6940e10daf
