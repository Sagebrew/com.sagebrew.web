from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_missions.endpoints import MissionViewSet

router = routers.SimpleRouter()
router.register(r'missions', MissionViewSet, base_name="mission")

urlpatterns = patterns(
    'sb_missions.endpoints',
    url(r'^', include(router.urls)),
    (r'^missions/', include('sb_goals.apis.relations.v1')),
    (r'^missions/', include('sb_updates.apis.relations.v1')),
    (r'^missions/', include('sb_donations.apis.relations.v1'))
)
