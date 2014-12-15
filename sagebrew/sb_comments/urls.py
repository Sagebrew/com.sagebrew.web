from django.conf.urls import patterns, url

from .views import (save_comment_view)

urlpatterns = patterns(
    'sb_comments.views',
    url(r'^submit_comment/$', save_comment_view, name="save_comment"),
)