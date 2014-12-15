from django.conf.urls import patterns, url

from .views import get_notifications

urlpatterns = patterns(
    'sb_notifications.views',
    url(r'^query_notifications/$', get_notifications, name="get_notifications"),
)