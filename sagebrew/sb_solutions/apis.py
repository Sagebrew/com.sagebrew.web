from django.conf.urls import patterns, url

from .endpoints import SolutionCommentList


urlpatterns = patterns(
    'sb_solutions.views',
    url(r'^(?P<uuid>[A-Za-z0-9.@_%+-]{36})/comments/$',
        SolutionCommentList.as_view(),
        name='solution-detail-comments'),
)