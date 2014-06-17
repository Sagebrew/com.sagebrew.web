from django.shortcuts import render, redirect
from django.http import HttpResponseServerError

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from .forms import InterestForm, ProfileInfoForm, AddressInfo
from .utils import generate_interests_tuple, validate_address


def profile_information(request):
    print request.POST
    profile_errors = None
    address_errors = None
    profile_information_form = ProfileInfoForm(request.POST or None)
    address_information_form = AddressInfo(request.POST or None)
    try:
        citizen = Pleb.index.get(email=request.user.email)
    except Pleb.DoesNotExist:
        redirect("404_Error")
    if profile_information_form.is_valid():
        print profile_information_form.cleaned_data
        #my_pleb = Pleb(**profile_information_form.cleaned_data)
        #my_pleb.save()
    else:
        profile_errors = profile_information_form.errors

    if address_information_form.is_valid():
        print address_information_form.cleaned_data
        if validate_address(address_information_form.cleaned_data):
            my_address = Address(**address_information_form.cleaned_data)
            my_address.save()
        else:
            print "Invalid Address"
        return redirect('interests')
    else:
        address_errors = address_information_form.errors

    return render(request, 'profile_info.html',
                    {'profile_information_form':profile_information_form,
                     'profile_info_errors': profile_errors,
                    'address_information_form':address_information_form,
                    'address_info_errors': address_errors})


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

    return render(request, 'invite_friends.html', {"here": None})