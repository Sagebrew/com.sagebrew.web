from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_goals.endpoints import (RoundViewSet)

router = routers.SimpleRouter()
router.register(r'rounds', RoundViewSet, base_name='round')

urlpatterns = patterns(
    'sb_goals.endpoints',
    url(r'^', include(router.urls)),
)
