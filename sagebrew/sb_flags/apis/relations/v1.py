from django.conf.urls import patterns, url

from sb_flags.endpoints import (ObjectFlagsListCreate,
                                ObjectFlagsRetrieveUpdateDestroy)


urlpatterns = patterns(
    'sb_flags.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/flags/$',
        ObjectFlagsListCreate.as_view()),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/flags/'
        r'(?P<flag_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectFlagsRetrieveUpdateDestroy.as_view()),
)
