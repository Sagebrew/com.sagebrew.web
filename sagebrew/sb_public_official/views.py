from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from sb_registration.utils import (verify_completed_registration)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def saga(request, username):
    representative = {"username": username}
    return render(request, 'action_page.html', {"representative":
                                                    representative,
                                                "registered": False})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def updates(request, username):
    representative = {"username": username}
    return render(request, 'action_page.html', {"representative":
                                                    representative,
                                                "registered": False})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def about(request, username):
    representative = {"username": username}
    return render(request, 'action_page.html', {"representative":
                                                    representative,
                                                "registered": False})