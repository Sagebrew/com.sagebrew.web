from django.conf.urls import patterns, url

from sb_updates.endpoints import (UpdateRetrieveUpdateDestroy)


urlpatterns = patterns(
    'sb_updates.endpoints',
    url(r'^updates/(?P<update_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        UpdateRetrieveUpdateDestroy.as_view(), name="update-detail")
)