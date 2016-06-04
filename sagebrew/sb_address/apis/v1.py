from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_address.endpoints import AddressViewSet

router = routers.SimpleRouter()
router.register(r'addresses', AddressViewSet, base_name="address")


urlpatterns = patterns(
    'sb_address.endpoints',
    url(r'^', include(router.urls)),
)
