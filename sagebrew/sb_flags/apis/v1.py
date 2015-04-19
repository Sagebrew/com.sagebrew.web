from django.conf.urls import patterns, url

from sb_flags.endpoints import (flag_list)

urlpatterns = patterns(
    'sb_flags.endpoints',
    url(r'^flags/$', flag_list, name="flag-list")
)
