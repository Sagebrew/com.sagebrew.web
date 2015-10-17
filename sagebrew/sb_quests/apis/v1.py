from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_quests.endpoints import (PoliticalCampaignViewSet, PositionViewSet)

router = routers.SimpleRouter()

router.register(r'campaigns', PoliticalCampaignViewSet, base_name='campaign')
router.register(r'positions', PositionViewSet, base_name='position')

urlpatterns = patterns(
    'sb_quests.endpoints',
    url(r'^', include(router.urls)),
    (r'^campaigns/', include('sb_goals.apis.relations.v1')),
    (r'^campaigns/', include('sb_updates.apis.relations.v1')),
    (r'^campaigns/', include('sb_donations.apis.relations.v1'))
)
