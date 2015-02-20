from django.conf.urls import url, patterns

from .views import create_badge, create_badge_api
urlpatterns = patterns(
    'sb_badges.views',
    url(r'^create_badge/$', create_badge, name='create_badge'),
    url(r'^create_badge_api/$', create_badge_api, name='create_badge_api')
)