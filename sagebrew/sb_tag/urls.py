from django.conf.urls import patterns, url

from .views import get_tag_view

urlpatterns = patterns(
    'sb_tag.views',
    url(r'^get_tags/q=(?P<query_param>[A-Za-z0-9.@_%+-]{1,1000})$',
        get_tag_view, name='get_tag_view')
)