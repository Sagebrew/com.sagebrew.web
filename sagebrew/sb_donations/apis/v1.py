from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_donations.endpoints import DonationViewSet


router = routers.SimpleRouter()
router.register(r'donations', DonationViewSet, base_name='donation')

urlpatterns = patterns(
    'sb_donations.endpoints',
    url(r'^', include(router.urls)),
)
