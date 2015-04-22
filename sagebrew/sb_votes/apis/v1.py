from django.conf.urls import patterns, url

from sb_votes.endpoints import (vote_list)


urlpatterns = patterns(
    'sb_votes.endpoints',
    url(r'^votes/$', vote_list, name="vote-list")
)
