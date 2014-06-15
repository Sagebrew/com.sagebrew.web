from django.shortcuts import render

from .forms import InterestForm

def profile_information(request):
    return render(request, 'profile_info.html',
                    {'profile_information_form':None})

def interests(request):
    interest_form = InterestForm(request.POST or None)
    if interest_form.is_valid():
        print "hello world"
    return render(request, 'interests.html', {'interest_form': interest_form})
