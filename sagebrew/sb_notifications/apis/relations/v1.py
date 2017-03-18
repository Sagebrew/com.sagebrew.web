from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_notifications.endpoints import UserNotificationViewSet
router = routers.SimpleRouter()
router.register(r'notifications', UserNotificationViewSet,
                base_name='notification')

urlpatterns = [
    url(r'^', include(router.urls)),
]
