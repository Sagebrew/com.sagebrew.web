from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from plebs.neo_models import Pleb
from sb_registration.utils import verify_completed_registration


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def council_page(request):
    if request.user.username == 'tyler_wiersing' \
            or request.user.username == 'devon_bleibtrey':
        return render(request, 'council_page.html')
    return redirect('profile_page', pleb_username=request.user.username)


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class CouncilView(LoginRequiredMixin):
    template_name = 'council_page.html'

    @method_decorator(user_passes_test(
        verify_completed_registration,
        login_url='/registration/profile_information'))
    def dispatch(self, *args, **kwargs):
        profile = Pleb.get(username=self.request.user.username)
        if self.request.user.username == 'tyler_wiersing' \
                or self.request.user.username == 'devon_bleibtrey' or \
                profile.reputation >= 10000:
            return super(CouncilView, self).dispatch(*args, **kwargs)
        return redirect('profile_page',
                        pleb_username=self.request.user.username)

    def get(self, request, object_uuid=None):
        return render(request, self.template_name)
