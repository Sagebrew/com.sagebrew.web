from django.conf.urls import patterns, url

from sb_solutions.views import QuestionSolutionList


urlpatterns = patterns(
    'sb_questions.views',
    url(r'^(?P<uuid>[A-Za-z0-9.@_%+-]{36})/solutions/$',
        QuestionSolutionList.as_view(),
        name='question-detail-solutions'),
)