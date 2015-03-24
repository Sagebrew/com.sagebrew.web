from django.conf.urls import patterns, url, include

from rest_framework import routers

from plebs.endpoints import UserViewSet

router = routers.SimpleRouter()

router.register(r'users', UserViewSet, base_name="users")

urlpatterns = patterns(
    'plebs.views',
    url(r'^', include(router.urls)),
)