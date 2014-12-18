from django.conf.urls import patterns, url

from .views import get_updates_from_dynamo

urlpatterns = patterns('sb_edits.views',
                       url(r'^update_neo_api/$', get_updates_from_dynamo,
                           name='update_neo'),
)