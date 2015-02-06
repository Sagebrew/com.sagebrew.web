from django.conf.urls import url, patterns

from .views import check_action

urlpatterns = patterns(
    'sb_privileges.views',
    url(r'^check/action/', check_action, name="check_action"),
)