from django.shortcuts import render



def profile_information(request):
    return render(request, 'profile_info.html',
                    {'profile_information_form':None})

def interests(request):
    return render(request, 'interests.html', {'interest_form':None})
