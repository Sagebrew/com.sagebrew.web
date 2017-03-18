from django.conf.urls import url

from sagebrew.sb_updates.endpoints import (UpdateListCreate)


urlpatterns = [
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/updates/$',
        UpdateListCreate.as_view(), name='update-list')
]
