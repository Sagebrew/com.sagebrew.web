from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_questions.endpoints import QuestionViewSet

router = routers.SimpleRouter()

router.register(r'questions', QuestionViewSet, base_name="question")

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^', include(router.urls)),
)