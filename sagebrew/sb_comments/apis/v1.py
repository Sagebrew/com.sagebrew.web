from django.conf.urls import url, include

from sagebrew.sb_comments.endpoints import (
    ObjectCommentsRetrieveUpdateDestroy, comment_list)

urlpatterns = [
    # This one handles deleting and editing comments
    url(r'^comments/(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(), name="comment-detail"),
    # Adding in for flags/votes/etc but must be a cleaner process
    url(r'^comments/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(), name="comment-detail"),
    url(r'^comments/$', comment_list, name="comment-list"),
    url(r'^comments/', include('sagebrew.sb_flags.apis.relations.v1')),
    url(r'^comments/', include('sagebrew.sb_votes.apis.relations.v1')),
]
