from django.conf.urls import patterns, url

from .views import (friend_request_answer)


urlpatterns = patterns('user_profiles.views',
    url(r'^friend_request/$', friend_request_answer),
)
