from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from sb_registration.utils import verify_completed_registration


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def council_page(request):
    return render(request, 'council_page.html')