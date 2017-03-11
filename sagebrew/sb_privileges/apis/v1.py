from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_privileges.endpoints import PrivilegeViewSet

router = routers.SimpleRouter()

router.register(r'privileges', PrivilegeViewSet, base_name="privilege")

urlpatterns = [
    url(r'^', include(router.urls)),
]
