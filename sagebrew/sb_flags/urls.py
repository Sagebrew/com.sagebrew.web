from django.conf.urls import patterns, url

from .views import flag_object_view

urlpatterns = patterns('sb_flags.views',
    url(r'^flag_object_api/$', flag_object_view, name="flag_object_api"),
)