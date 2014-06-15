from django.shortcuts import render
from django.http import HttpResponseServerError

from plebs.neo_models import Pleb, TopicCategory, SBTopic

from .forms import InterestForm

def profile_information(request):
    return render(request, 'profile_info.html',
                    {'profile_information_form':None})

def interests(request):
    interest_form = InterestForm(request.POST or None)

    cat_instance = TopicCategory.category()
    categories = cat_instance.instance.all()
    topic_selection = {}
    specific_interest_choices = []
    for category in categories:
        topic_selection[category.title] = category.sb_topics.all()
        for item in topic_selection[category.title]:
            specific_interest_choices.append((item.title, item.title))

    interest_form.fields["specific_interests"].choices = specific_interest_choices
    print request.POST
    if interest_form.is_valid():
        for item in interest_form.cleaned_data:
            print interest_form.cleaned_data[item]
            if(interest_form.cleaned_data[item]):
                try:
                    citizen = Pleb.index.get(email=request.user.email)
                except Pleb.DoesNotExist:
                    # return HttpResponseServerError('<h1>Server Error (500)</h1>')
                    print "Pleb does not exist"
                try:
                    interest_object = TopicCategory.index.get(title=item)
                except TopicCategory.DoesNotExist:
                    # return HttpResponseServerError('<h1>Server Error (500)</h1>')
                    print "Topic cat does not exist"
                # citizen.interest.connect(interest_object)
    else:
        print interest_form.errors

    return render(request, 'interests.html', {'interest_form': interest_form,
                                              "topics": topic_selection})