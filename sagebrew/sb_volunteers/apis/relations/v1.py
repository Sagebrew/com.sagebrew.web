from django.conf.urls import patterns, url, include
from rest_framework import routers

from sb_volunteers.endpoints import VolunteerViewSet

router = routers.SimpleRouter()
router.register(r'volunteers', VolunteerViewSet, base_name="volunteer")

urlpatterns = patterns(
    'sb_donations.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/', include(router.urls)),
)
