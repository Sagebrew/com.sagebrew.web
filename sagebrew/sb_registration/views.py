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
    specific_interest_choices = []
    for category in categories:
        for item in category.sb_topics.all():
            specific_interest_choices.append((item.title, item.title))

    interest_form.fields["specific_interests"].choices = specific_interest_choices
    if interest_form.is_valid():
        for item in interest_form.cleaned_data:
            if(interest_form.cleaned_data[item] and
                       item != "specific_interests"):
                try:
                    citizen = Pleb.index.get(email=request.user.email)
                except Pleb.DoesNotExist:
                    # return HttpResponseServerError('<h1>Server Error (500)</h1>')
                    print "Pleb does not exist"
                try:
                    print item
                    category_object = TopicCategory.index.get(
                        title=item.capitalize())
                except TopicCategory.DoesNotExist:
                    # return HttpResponseServerError('<h1>Server Error (500)</h1>')
                    print "Topic cat does not exist"
                # citizen.topic_category.connect(category_object)
        for topic in interest_form.cleaned_data["specific_interests"]:
            try:
                interest_object = SBTopic.index.get(title=topic)
                print interest_object.title
            except SBTopic.DoesNotExist:
                # return HttpResponseServerError('<h1>Server Error (500)</h1>')
                print "Topic cat does not exist"
            # citizen.sb_topics.connect(interest_object)
    else:
        print interest_form.errors

    return render(request, 'interests.html', {'interest_form': interest_form})