from django.conf.urls import patterns, url, include

from rest_framework import routers


router = routers.SimpleRouter()


urlpatterns = patterns(
    'sb_missions.endpoints',
    url(r'^', include(router.urls)),
)
