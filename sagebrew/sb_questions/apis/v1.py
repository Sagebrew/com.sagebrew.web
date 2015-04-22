from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_questions.endpoints import QuestionViewSet

from sb_solutions.endpoints import (ObjectSolutionsListCreate,
                                    ObjectSolutionsRetrieveUpdateDestroy,
                                    solution_renderer)


router = routers.SimpleRouter()
router.register(r'questions', QuestionViewSet, base_name="question")


urlpatterns = patterns(
    'sb_questions.endpoints',
    url(r'^', include(router.urls)),
    # Solutions
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/solutions/$',
        ObjectSolutionsListCreate.as_view(), name="question-solutions"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'solutions/render/$',
        solution_renderer, name="question-solution-html"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/solutions/'
        r'(?P<solution_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectSolutionsRetrieveUpdateDestroy.as_view(),
        name="question-solution"),
    (r'^questions/', include('sb_comments.apis.relations.v1')),
    (r'^questions/', include('sb_flags.apis.relations.v1')),
    (r'^questions/', include('sb_votes.apis.relations.v1')),
)
