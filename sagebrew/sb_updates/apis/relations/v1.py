from django.conf.urls import patterns, url

from sb_updates.endpoints import (UpdateListCreate, update_renderer)


urlpatterns = patterns(
    'sb_updates.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/updates/$',
        UpdateListCreate.as_view(), name='update-list'),
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/'
        r'updates/render/$', update_renderer, name='update-render'),
)
