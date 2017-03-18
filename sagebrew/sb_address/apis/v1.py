from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_address.endpoints import AddressViewSet

router = routers.SimpleRouter()
router.register(r'addresses', AddressViewSet, base_name="address")


urlpatterns = [
    url(r'^', include(router.urls)),
]
