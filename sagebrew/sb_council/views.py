from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from sb_registration.utils import verify_completed_registration

from logging import getLogger
logger = getLogger('loggly_logs')


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def council_page(request):
    if request.user.username == 'tyler_wiersing' \
            or request.user.username == 'devon_bleibtrey':
        return render(request, 'council_page.html')
    return redirect('profile_page', pleb_username=request.user.username)
