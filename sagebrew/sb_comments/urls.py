from django.conf.urls import patterns, url

from .views import (save_comment_view, get_comments, edit_comment,
                    vote_comment, flag_comment, delete_comment)

urlpatterns = patterns(
    'sb_comments.views',
    url(r'^submit_comment/$', save_comment_view, name="save_comment"),
    url(r'^query_comments/$', get_comments, name="get_comments"),
    url(r'^edit_comment/$', edit_comment, name="edit_comment"),
    url(r'^vote_comment/$', vote_comment, name="vote_comment"),
    url(r'^delete_comment/$', delete_comment, name="delete_comment"),
    url(r'^flag_comment/$', flag_comment, name="flag_comment")
)