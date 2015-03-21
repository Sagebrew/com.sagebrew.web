from django.conf.urls import patterns, url

from sb_solutions.endpoints import QuestionSolutionsList


urlpatterns = patterns(
    'sb_questions.views',
    url(r'^(?P<uuid>[A-Za-z0-9.@_%+-]{36})/solutions/$',
        QuestionSolutionsList.as_view(),
        name='question-detail-solutions'),
)