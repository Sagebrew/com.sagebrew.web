from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_council.endpoints import CouncilObjectEndpoint

router = routers.SimpleRouter()

router.register(r'council', CouncilObjectEndpoint, base_name='council')

urlpatterns = [
    url(r'^', include(router.urls)),
]
