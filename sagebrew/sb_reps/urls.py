from django.conf.urls import url, patterns

from .views import representative_page

urlpatterns = patterns(
    'sb_votes.views',
    url(r'^(?P<rep_id>[A-Za-z0-9.@_%+-]{7,60})/$', representative_page,
        name="rep_page"))