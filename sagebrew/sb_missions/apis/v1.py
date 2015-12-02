from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_missions.endpoints import MissionViewSet

router = routers.SimpleRouter()
router.register(r'missions', MissionViewSet, base_name="mission")

urlpatterns = patterns(
    'sb_missions.endpoints',
    url(r'^', include(router.urls)),
)
