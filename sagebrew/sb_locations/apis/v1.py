from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_locations.endpoints import LocationList

router = routers.SimpleRouter()

router.register(r'locations', LocationList, base_name='location')

urlpatterns = patterns(
    'sb_locations.endpoints',
    url(r'^', include(router.urls)),
)
