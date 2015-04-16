from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_privileges.endpoints import PrivilegeViewSet

router = routers.SimpleRouter()

router.register(r'privileges', PrivilegeViewSet, base_name="privilege")

urlpatterns = patterns(
    'sb_privileges.endpoints',
    url(r'^', include(router.urls)),
)