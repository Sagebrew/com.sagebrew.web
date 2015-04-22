from django.conf.urls import patterns, url, include

from sb_comments.endpoints import (ObjectCommentsRetrieveUpdateDestroy,
                                   comment_list)

urlpatterns = patterns(
    'sb_comments.endpoints',
    url(r'^comments/(?P<comment_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(), name="comment-detail"),
    # Adding in for flags/votes/etc but must be a cleaner process
    url(r'^comments/(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        ObjectCommentsRetrieveUpdateDestroy.as_view(), name="comment-detail"),
    url(r'^comments/$', comment_list, name="comment-list"),
    (r'^comments/', include('sb_flags.apis.relations.v1')),
    (r'^comments/', include('sb_votes.apis.relations.v1')),
)
