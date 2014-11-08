from django.conf.urls import patterns, url

from .views import (save_comment_view, get_comments,
                    delete_comment)

urlpatterns = patterns(
    'sb_comments.views',
    url(r'^submit_comment/$', save_comment_view, name="save_comment"),
    url(r'^query_comments/$', get_comments, name="get_comments"),
    url(r'^delete_comment/$', delete_comment, name="delete_comment"),
)