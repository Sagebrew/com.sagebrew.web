from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_questions.endpoints import QuestionViewSet
from sb_comments.endpoints import (ObjectCommentsListCreate,
                                   ObjectCommentsRetrieveUpdateDestroy,
                                   comment_renderer)

router = routers.SimpleRouter()

router.register(r'questions', QuestionViewSet, base_name="question")

urlpatterns = patterns(
    'sb_questions.endpoints',
    url(r'^', include(router.urls)),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/$',
        ObjectCommentsListCreate.as_view(), name="question-comments"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'comments/render/$',
        comment_renderer, name="question-comments-html"),
    url(r'^questions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/'
        r'(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(),
        name="question-comment"),
)