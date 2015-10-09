from django.conf.urls import patterns, url

from .views import edit_update, create_update, updates


urlpatterns = patterns(
    'sb_updates.views',
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/updates/$', updates,
        name='quest_updates'),
    url(r'^([A-Za-z0-9.@_%+-]{2,36})/updates/'
        r'(?P<object_uuid>[A-Za-z0-9.@_%+-]{1,36})/edit/$',
        edit_update, name='update-edit'),
    url(r'^(?P<username>[A-Za-z0-9.@_%+-]{2,36})/create_update/$',
        create_update, name="create_update"),
)
