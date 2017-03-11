from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_donations.endpoints import DonationViewSet, sagebrew_donation


router = routers.SimpleRouter()
router.register(r'donations', DonationViewSet, base_name='donation')

urlpatterns = [
    url(r'^donations/sagebrew_donations/$', sagebrew_donation,
        name="direct_donation"),
    url(r'^', include(router.urls)),
]
