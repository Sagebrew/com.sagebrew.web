from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_solutions.endpoints import SolutionViewSet

router = routers.SimpleRouter()

router.register(r'solutions', SolutionViewSet, base_name="solution")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^solutions/', include('sagebrew.sb_comments.apis.relations.v1')),
    url(r'^solutions/', include('sagebrew.sb_flags.apis.relations.v1')),
    url(r'^solutions/', include('sagebrew.sb_votes.apis.relations.v1')),
]
