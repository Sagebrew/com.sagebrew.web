from django.conf.urls import patterns, url

from .views import (get_friend_requests, create_friend_request,
                    respond_friend_request)

urlpatterns = patterns(
    'plebs.views',
    url(r'^query_friend_requests/$', get_friend_requests,
        name="get_friend_requests"),
    url(r'^create_friend_request/$', create_friend_request,
        name="create_friend_request"),
    url(r'^respond_friend_request/$', respond_friend_request,
        name="respond_friend_request"),
)
