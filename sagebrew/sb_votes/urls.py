from django.conf.urls import url, patterns

from .views import vote_object_view

urlpatterns = patterns(
    'sb_votes.views',
    url(r'^vote_object_api/$', vote_object_view, name="vote_object_api"))

