from django.shortcuts import render
from django.http import HttpResponseServerError

from plebs.neo_models import Pleb, TopicCategory

from .forms import InterestForm

def profile_information(request):
    return render(request, 'profile_info.html',
                    {'profile_information_form':None})

def interests(request):
    interest_form = InterestForm(request.POST or None)
    if interest_form.is_valid():
        for item in interest_form.cleaned_data:
            if(interest_form.cleaned_data[item]):
                try:
                    citizen = Pleb.index.get(sb_email=request.user.email)
                except Pleb.DoesNotExist:
                    raise HttpResponseServerError
                try:
                    interest_object = TopicCategory.index.get(tite=item)
                except TopicCategory.DoesNotExist:
                    raise HttpResponseServerError
                citizen.interest.connect(interest_object)

    return render(request, 'interests.html', {'interest_form': interest_form})