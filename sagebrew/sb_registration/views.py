import os

from django.conf import settings
from uuid import uuid1
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from .forms import (ProfileInfoForm, AddressInfoForm, InterestForm, ProfilePictureForm,
                    ProfilePageForm, AddressChoiceForm)
from .utils import (validate_address, generate_interests_tuple, upload_image,
                    compare_address, determine_congressmen)

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
        citizen.date_of_birth = profile_information_form.cleaned_data['date_of_birth']
        citizen.save()
        print profile_information_form.cleaned_data
        #my_pleb = Pleb(**profile_information_form.cleaned_data)
        #my_pleb.save()

    if address_information_form.is_valid():
        input_address_dict = address_information_form.cleaned_data
        valid_address_dict = validate_address(address_information_form.cleaned_data)
        if valid_address_dict:
            input_address_dict['district'] = valid_address_dict[0]["metadata"]["congressional_district"]
            my_address = Address(**address_information_form.cleaned_data)
            my_address.save()
            citizen.completed_profile_info = True
            citizen.save()
            citizen.address.connect(my_address)
            return redirect('interests')
    '''
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
    '''

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


@login_required()
def profile_picture(request):
    if request.method == 'POST':
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)
        if profile_picture_form.is_valid():
            try:
                citizen = Pleb.index.get(email=request.user.email)
                #if citizen.completed_profile_info:
                #    return redirect('profile_page')
                #print citizen.profile_pic
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
    profile_page_form = ProfilePageForm(request.GET or None)
    citizen = Pleb.index.get(email=request.user.email)
    determine_congressmen(citizen.address)

    return render(request, 'profile_page.html', {'profile_page_form': profile_page_form,
                                                 'pleb_info': citizen})

