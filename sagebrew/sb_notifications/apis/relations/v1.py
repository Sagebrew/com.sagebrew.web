from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_notifications.endpoints import UserNotificationViewSet
router = routers.SimpleRouter()
router.register(r'notifications', UserNotificationViewSet,
                base_name='notification')

urlpatterns = patterns(
    'sb_notifications.endpoints',
    url(r'^', include(router.urls)),

)
