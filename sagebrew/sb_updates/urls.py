from django.conf.urls import patterns, url

from .views import edit_update


urlpatterns = patterns(
    'sb_updates.views',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{1,36})/edit/$',
        edit_update, name='update-edit')
)
