from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_locations.endpoints import (LocationList)

router = routers.SimpleRouter()

router.register(r'locations', LocationList, base_name='location')

urlpatterns = [
    url(r'^', include(router.urls)),
]
