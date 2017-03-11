from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_questions.endpoints import QuestionViewSet

from sagebrew.sb_solutions.endpoints import (
    ObjectSolutionsListCreate, ObjectSolutionsRetrieveUpdateDestroy)


router = routers.SimpleRouter()
router.register(r'questions', QuestionViewSet, base_name="question")


urlpatterns = [
    url(r'^', include(router.urls)),
    # Solutions
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/solutions/$',
        ObjectSolutionsListCreate.as_view(), name="question-solutions"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/solutions/'
        r'(?P<solution_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectSolutionsRetrieveUpdateDestroy.as_view(),
        name="question-solution"),
    url(r'^questions/', include('sagebrew.sb_comments.apis.relations.v1')),
    url(r'^questions/', include('sagebrew.sb_flags.apis.relations.v1')),
    url(r'^questions/', include('sagebrew.sb_votes.apis.relations.v1')),
]
