from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_donations.endpoints import DonationViewSet, sagebrew_donation


router = routers.SimpleRouter()
router.register(r'donations', DonationViewSet, base_name='donation')

urlpatterns = patterns(
    'sb_donations.endpoints',
    url(r'^donations/sagebrew_donations/$', sagebrew_donation,
        name="direct_donation"),
    url(r'^', include(router.urls)),

)
