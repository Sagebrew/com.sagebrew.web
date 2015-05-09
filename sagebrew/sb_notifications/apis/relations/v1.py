from django.conf.urls import patterns, url

from sb_notifications.endpoints import (UserNotificationList,
                                        UserNotificationRetrieve)


urlpatterns = patterns(
    'sb_notifications.endpoints',
    url(r'^notifications/$',
        UserNotificationList.as_view()),
    url(r'^notifications/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        UserNotificationRetrieve.as_view()),
)
