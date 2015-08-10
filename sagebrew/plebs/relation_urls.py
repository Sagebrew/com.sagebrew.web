from django.conf.urls import patterns, url

from .views import (create_friend_request)

urlpatterns = patterns(
    'plebs.views',
    url(r'^create_friend_request/$', create_friend_request,
        name="create_friend_request")
)
