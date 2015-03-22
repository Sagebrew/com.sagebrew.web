from django.conf.urls import patterns, url, include

from rest_framework import routers

from .endpoints import QuestionViewSet

router = routers.SimpleRouter()

router.register(r'questions', QuestionViewSet, base_name="questions")

urlpatterns = patterns(
    'sb_questions.views',
    url(r'^', include(router.urls)),
)