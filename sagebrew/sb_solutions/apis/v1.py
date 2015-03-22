from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_solutions.endpoints import SolutionViewSet

router = routers.SimpleRouter()

router.register(r'solutions', SolutionViewSet, base_name="solutions")

urlpatterns = patterns(
    'sb_solutions.views',
    url(r'^', include(router.urls)),
)