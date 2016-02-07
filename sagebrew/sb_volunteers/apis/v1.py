from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_volunteers.endpoints import VolunteerViewSet

router = routers.SimpleRouter()

router.register(r'volunteers', VolunteerViewSet, base_name="volunteer")


urlpatterns = patterns(
    'sb_volunteers.endpoints',
    url(r'^', include(router.urls)),
)
