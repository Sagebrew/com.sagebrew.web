from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_solutions.endpoints import SolutionViewSet

router = routers.SimpleRouter()

router.register(r'solutions', SolutionViewSet, base_name="solution")

urlpatterns = patterns(
    'sb_solutions.endpoints',
    url(r'^', include(router.urls)),
    (r'^solutions/', include('sb_comments.apis.relations.v1')),
    (r'^solutions/', include('sb_flags.apis.relations.v1')),
)