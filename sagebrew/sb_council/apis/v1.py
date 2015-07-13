from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_council.endpoints import CouncilObjectEndpoint

router = routers.SimpleRouter()

router.register(r'council', CouncilObjectEndpoint, base_name='council')

urlpatterns = patterns(
    'sb_council.endpoints',
    url(r'^', include(router.urls)),
)
