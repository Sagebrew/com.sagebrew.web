from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from sb_docstore.utils import get_rep_docs
from sb_registration.utils import (verify_completed_registration)


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def saga(request, username):
    representative = {"username": username}
    res = get_rep_docs(username)
    rep = dict(res['rep'])
    print rep
    return render(request, 'action_page.html', {"representative":
                                                    rep,
                                                "registered": False})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def updates(request, username):
    representative = {"username": username}
    res = get_rep_docs(username)
    rep = dict(res['rep'])
    return render(request, 'action_page.html', {"representative":
                                                    rep,
                                                "registered": False})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def about(request, username):
    representative = {"username": username}
    res = get_rep_docs(username)
    rep = dict(res['rep'])
    return render(request, 'action_page.html', {"representative":
                                                    rep,
                                                "registered": False})