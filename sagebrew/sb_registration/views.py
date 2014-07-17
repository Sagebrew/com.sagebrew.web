import os
import hashlib
from json import dumps

from django.conf import settings
from uuid import uuid1
from requests import post as request_post
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.models import User

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from .forms import (ProfileInfoForm, AddressInfoForm, InterestForm, ProfilePictureForm,
                    ProfilePageForm, AddressChoiceForm)
from .utils import (validate_address, generate_interests_tuple, upload_image,
                    compare_address, generate_address_tuple,
                    determine_senators, determine_reps, create_address_string,
                    create_address_long_hash)


@login_required
def profile_information(request):
    '''
    Creates both a ProfileInfoForm and AddressInfoForm which populates the
    fields with what the user enters. If this function gets a valid POST request it
    will update the pleb. It then validates the address, through smartystreets api,
    if the address is valid a Address neo_model is created and populated.


    COMPLETED THIS TASK BUT STILL NEED TO PUT SOME COMMENTS AROUND IT
    Need to use a hash to verify the same address string is being
    used instead of an int. That way if smarty streets passes back
    the addresses in a different order we can use the same address
    we provided the user previously based on the previous
    smarty streets ordering.
    '''
    profile_information_form = ProfileInfoForm(request.POST or None)
    address_information_form = AddressInfoForm(request.POST or None)
    address_selection_form = AddressChoiceForm(request.POST or None)
    address_selection = "no_selection"
    try:
        citizen = Pleb.index.get(email=request.user.email)
    except Pleb.DoesNotExist:
        return redirect("404_Error")
    if profile_information_form.is_valid():
        citizen.date_of_birth = profile_information_form.cleaned_data[
            "date_of_birth"]
        citizen.home_town = profile_information_form.cleaned_data["home_town"]
        citizen.high_school = profile_information_form.cleaned_data[
            "high_school"]
        citizen.college = profile_information_form.cleaned_data["college"]
        citizen.employer = profile_information_form.cleaned_data["employer"]
        citizen.save()

    if address_information_form.is_valid():
        address_clean = address_information_form.cleaned_data
        address_info = validate_address(address_clean)
        addresses_returned = len(address_info)
        address_tuple = generate_address_tuple(address_info)

        # Not doing 0 cause already done with address_information_form
        if(addresses_returned == 1):
            if compare_address(address_info[0], address_clean):
                address_info[0]["country"] = "USA"
                address_long_hash = create_address_long_hash(
                        address_info[0])
                try:
                    address = Address.index.get(address_hash=address_long_hash)
                except Address.DoesNotExist:
                    address_info[0]["address_hash"] = address_long_hash
                    address = Address(**address_info[0])
                    address.save()
                address.address.connect(citizen)
                citizen.completed_profile_info = True
                citizen.address.connect(address)
                citizen.save()
                return redirect('interests')
            else:
                address_selection_form.fields['address_options'].choices = address_tuple
                address_selection_form.fields['address_options'].required = True
                address_selection = "selection"
        elif(addresses_returned > 1):
            # Choices need to be populated prior to is_valid call to ensure
            # that the form validates against the correct values
            # We also are able ot keep this in the same location because
            # we hid the other address form but it keeps the same values as
            # previously entered. This enables us to get the same results
            # back from smarty streets and validate those choices again then
            # select the one that the user selected.
            address_selection_form.fields['address_options'].choices = address_tuple
            address_selection_form.fields['address_options'].required = True
            address_selection = "selection"

        if(address_selection == "selection"):
            if(address_selection_form.is_valid()):
                store_address = None
                address_hash = address_selection_form.cleaned_data[
                    "address_options"]
                for optional_address in address_info:
                    optional_address["country"] = "USA"
                    address_string = create_address_string(optional_address)
                    optional_hash = hashlib.sha224(address_string).hexdigest()
                    if(address_hash == optional_hash):
                        store_address = optional_address
                        break
                if(store_address is not None):
                    address_long_hash = create_address_long_hash(store_address)
                    try:
                        address = Address.index.get(address_hash=address_long_hash)
                    except Address.DoesNotExist:
                        store_address["address_hash"] = address_long_hash
                        address = Address(**store_address)
                        address.save()
                    address.address.connect(citizen)
                    citizen.completed_profile_info = True
                    citizen.address.connect(address)
                    citizen.save()
                    return redirect('interests')

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
                    # TODO profile page profile picture
                    if citizen.completed_profile_info:
                        return redirect('profile_picture')
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


@login_required()
def profile_picture(request):
    '''
    The profile picture view accepts an image from the user, which is stored in
    the TEMP_FILES directory until it is uploaded to s3 after which the locally
    stored tempfile is deleted. After the url of the image is returned from
    the upload_image util the url is stored as the profile_picture field in the Pleb
    model.
`
    :param request:
    :return:
    '''
    if request.method == 'POST':
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)
        if profile_picture_form.is_valid():
            try:
                citizen = Pleb.index.get(email=request.user.email)
                #if citizen.completed_profile_info:
                #    return redirect('profile_page')
                #print citizen.profile_pic
            except Pleb.DoesNotExist:
                return render(request, 'profile_picture.html', {'profile_picture_form': profile_picture_form})
            image_uuid = uuid1()
            data = request.FILES['picture']
            temp_file = '%s%s.jpeg' % (settings.TEMP_FILES, image_uuid)
            with open(temp_file, 'wb+') as destination:
                for chunk in data.chunks():
                    destination.write(chunk)
            citizen.profile_pic = upload_image('profile_pictures', image_uuid)
            citizen.save()
            return redirect('/registration/profile_page/' + citizen.email)#citizen.first_name+'_'+citizen.last_name)
    else:
        profile_picture_form = ProfilePictureForm()
    return render(request, 'profile_picture.html', {'profile_picture_form': profile_picture_form})

@login_required()
def profile_page(request, pleb_email):
    '''
    Displays the users profile_page. This is where we call the functions to determine
    who the senators are for the plebs state and which representative for the plebs
    district

    :param request:
    :return:
    '''
    citizen = Pleb.index.get(email=pleb_email)
    current_user = request.user
    page_user = User.objects.get(email = pleb_email)
    is_owner = False
    is_friend = False
    friends_list = citizen.traverse('friends').run()
    if current_user.email == page_user.email:
        is_owner = True
    #TODO traversal to see if current_user is a friend of page_user
    elif citizen.traverse('friends').where('email','=',current_user.email).run():
        is_friend = True

    print "is owner", is_owner
    print "is friend", is_friend
    profile_page_form = ProfilePageForm(request.GET or None)
    print citizen.traverse('friends').where('email','=',current_user.email).run()
    # TODO check for index error
    # TODO check why address does not always work
    # TODO deal with address and senator/rep in a util + task
    #address = citizen.traverse('address').run()[0]
    #sen_array = determine_senators(address)
    #rep_array = determine_reps(address)
    post_data = {'email': citizen.email}
    headers = {'content-type': 'application/json'}
    post_req = request_post('https://192.168.56.101/posts/query_posts/',
                            data=dumps(post_data), verify=False, headers=headers)
    user_posts = post_req.json()
    notification_req = request_post('https://192.168.56.101/notifications/query_notifications/',
                                    data=dumps(post_data), verify=False, headers=headers)
    user_notifications = notification_req.json()
    friend_requests_req = request_post('https://192.168.56.101/notifications/query_friend_requests/',
                                       data=dumps(post_data), verify=False, headers=headers)
    user_friend_requests = friend_requests_req.json()

    return render(request, 'profile_page.html', {'profile_page_form': profile_page_form,
                                                 'pleb_info': citizen,
                                                 'current_user': current_user.email,
                                                 'page_user': page_user.email,
                                                 #'senator_names': sen_array,
                                                 #'rep_name': rep_array,
                                                 'user_posts': user_posts,
                                                 'user_notifications': user_notifications,
                                                 #'user_friend_requests': user_friend_requests,
                                                 'is_owner': is_owner,
                                                 'is_friend': is_friend,})
                                                 #'post_comments': post_comments})
