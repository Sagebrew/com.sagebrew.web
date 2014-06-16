from django.shortcuts import render, redirect
from django.http import HttpResponseServerError

from plebs.neo_models import Pleb, TopicCategory, SBTopic

from .forms import InterestForm
from .utils import generate_interests_tuple


def profile_information(request):
    return render(request, 'profile_info.html',
                    {'profile_information_form':None})


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
                    # return HttpResponseServerError('')
                    print "Pleb does not exist"
                try:
                    print item
                    category_object = TopicCategory.index.get(
                        title=item.capitalize())
                    for topic in category_object.sb_topics.all():
                        #citizen.sb_topics.connect(topic)
                        pass
                    # citizen.topic_category.connect(category_object)
                except TopicCategory.DoesNotExist:
                    # return HttpResponseServerError('')
                    print "Topic cat does not exist"

        for topic in interest_form.cleaned_data["specific_interests"]:
            try:
                interest_object = SBTopic.index.get(title=topic)
                print interest_object.title
            except SBTopic.DoesNotExist:
                # return HttpResponseServerError('')
                print "Topic cat does not exist"
            # citizen.sb_topics.connect(interest_object)
        return redirect('invite_friends')
    else:
        print interest_form.errors

    return render(request, 'interests.html', {'interest_form': interest_form})


def invite_friends(request):

    return render(request, 'invite_friends.html', {"here": None})