from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_locations.endpoints import LocationList, render_positions

router = routers.SimpleRouter()

router.register(r'locations', LocationList, base_name='location')

urlpatterns = patterns(
    'sb_locations.endpoints',
    url(r'^', include(router.urls)),
    url(r'^locations/(?P<name>[\w|\W]{1,40})/positions/render/$',
        render_positions, name="render_positions"),
)
