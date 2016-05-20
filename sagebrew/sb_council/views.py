from django.conf import settings
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from plebs.neo_models import Pleb


class LoginRequiredMixin(View):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class CouncilView(LoginRequiredMixin):
    template_name = 'council_page.html'

    def dispatch(self, *args, **kwargs):
        profile = Pleb.get(username=self.request.user.username)
        if self.request.user.username == 'tyler_wiersing' \
                or self.request.user.username == 'devon_bleibtrey' or \
                profile.reputation >= 10000:
            return super(CouncilView, self).dispatch(*args, **kwargs)
        return redirect('profile_page',
                        pleb_username=self.request.user.username)

    def get(self, request, object_uuid=None):
        return render(request, self.template_name,
                      {"review_feedback":
                           dict(settings.REVIEW_FEEDBACK_OPTIONS)})
