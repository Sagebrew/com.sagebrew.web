from django.conf.urls import patterns, url

from .views import council_page

urlpatterns = patterns(
    'sb_council.views',
    url(r'^$', council_page, name='council_page'),
)
