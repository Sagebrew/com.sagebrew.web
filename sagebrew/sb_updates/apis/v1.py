from django.conf.urls import url

from sagebrew.sb_updates.endpoints import (UpdateRetrieveUpdateDestroy)


urlpatterns = [
    url(r'^updates/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        UpdateRetrieveUpdateDestroy.as_view(), name="update-detail")
]
