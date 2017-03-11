from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_missions.endpoints import MissionViewSet

router = routers.SimpleRouter()
router.register(r'missions', MissionViewSet, base_name="mission")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^missions/', include('sagebrew.sb_updates.apis.relations.v1')),
    url(r'^missions/', include('sagebrew.sb_donations.apis.relations.v1')),
    url(r'^missions/', include('sagebrew.sb_volunteers.apis.relations.v1')),
    url(r'^missions/', include('sagebrew.sb_gifts.apis.relations.v1'))
]
