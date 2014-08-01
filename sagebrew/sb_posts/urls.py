from django.conf.urls import patterns, url

from .views import (save_post_view, get_user_posts, edit_post, delete_post,
                    vote_post)

urlpatterns = patterns('sb_posts.views',
                       url(r'^submit_post/$', save_post_view,
                           name="save_post"),
                       url(r'^query_posts/$', get_user_posts,
                           name="get_user_posts"),
                       url(r'^edit_post/$', edit_post, name="edit_post"),
                       url(r'^delete_post/$', delete_post, name="delete_post"),
                       url(r'^vote_post/$', vote_post, name="vote_post")
)