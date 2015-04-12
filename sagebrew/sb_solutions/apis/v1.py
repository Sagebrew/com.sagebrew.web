from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_solutions.endpoints import SolutionViewSet
from sb_comments.endpoints import (ObjectCommentsListCreate,
                                   ObjectCommentsRetrieveUpdateDestroy,
                                   comment_renderer)

from sb_flags.endpoints import (ObjectFlagsListCreate,
                                ObjectFlagsRetrieveUpdateDestroy,
                                flag_renderer)

router = routers.SimpleRouter()

router.register(r'solutions', SolutionViewSet, base_name="solution")

urlpatterns = patterns(
    'sb_solutions.endpoints',
    url(r'^', include(router.urls)),
    url(r'^solutions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/$',
        ObjectCommentsListCreate.as_view(), name="question-comments"),
    url(r'^solutions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'comments/render/$',
        comment_renderer, name="question-comments-html"),
    url(r'^solutions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/comments/'
        r'(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(),
        name="question-comment"),

    # Flags
    url(r'^solutions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/flags/$',
        ObjectFlagsListCreate.as_view(), name="solution-flags"),
    url(r'^solutions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/'
        r'flags/render/$',
        flag_renderer, name="solution-flag-html"),
    url(r'^solutions/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/flags/'
        r'(?P<flag_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectFlagsRetrieveUpdateDestroy.as_view(),
        name="solution-flag"),
)