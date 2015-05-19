from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_campaigns.endpoints import (PoliticalCampaignViewSet,)

router = routers.SimpleRouter()

router.register(r'campaigns', PoliticalCampaignViewSet, base_name='campaign')

urlpatterns = patterns(
    'sb_campaigns.endpoints',
    url(r'^', include(router.urls)),
    (r'^campaigns/', include('sb_goals.apis.relations.v1')),
    (r'^campaigns/', include('sb_votes.apis.relations.v1')),
)
