from django.conf.urls import patterns, url

from .views import (save_post_view, get_user_posts, delete_post)

urlpatterns = patterns(
    'sb_posts.views',
    url(r'^submit_post/$', save_post_view, name="save_post"),
    url(r'^query_posts/$', get_user_posts, name="get_user_posts"),
    url(r'^delete_post/$', delete_post, name="delete_post"),
)