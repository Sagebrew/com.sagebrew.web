from django.conf.urls import patterns, url

from .views import get_notifications, create_notification

urlpatterns = patterns(
    'sb_notifications.views',
    url(r'^query_notifications/$', get_notifications,
        name="get_notifications"),
    url(r'^create_notification/$', create_notification,
        name="create_notification")
)