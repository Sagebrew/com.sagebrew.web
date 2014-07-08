from django.conf.urls import patterns, url

from .views import get_notifications, get_friend_requests, create_notification,create_friend_request

urlpatterns = patterns('sb_notifications.views',
    url(r'^query_notifications/$', get_notifications, name="get_notifications"),
    url(r'^query_friend_requests/$', get_friend_requests, name="get_friend_requests"),
    url(r'^create_notification/$', create_notification, name="create_notification"),
    url(r'^create_friend_request/$', create_friend_request, name="create_friend_request")
)