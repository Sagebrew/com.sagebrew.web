from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_counsel.endpoints import CounselObjectEndpoint

router = routers.SimpleRouter()

router.register(r'counsel', CounselObjectEndpoint, base_name='counsel')

urlpatterns = patterns(
    'sb_campaigns.endpoints',
    url(r'^', include(router.urls)),
)
