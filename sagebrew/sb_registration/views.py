import os

from uuid import uuid1
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from .forms import ProfileInfoForm, AddressInfoForm, InterestForm, ProfilePictureForm
from .utils import validate_address, generate_interests_tuple, upload_image

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
        return redirect('profile_picture')

    return render(request, 'interests.html', {'interest_form': interest_form})



def profile_picture(request):
    if request.method == 'POST':
        print 'here'
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)
        print profile_picture_form
        if profile_picture_form.is_valid():
            try:
                citizen = Pleb.index.get(email=request.user.email)
            except Pleb.DoesNotExist:
                print("How the hell did you even get here!?")
            image_uuid = uuid1()
            print upload_image('/profile_pictures',image_uuid)
    else:
        profile_picture_form = ProfilePictureForm()
    return render(request, 'profile_picture.html', {'profile_picture_form': profile_picture_form})

