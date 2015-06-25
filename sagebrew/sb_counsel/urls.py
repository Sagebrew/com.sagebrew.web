from django.conf.urls import patterns, url

from .views import counsel_page

urlpatterns = patterns(
    'sb_counsel.views',
    url(r'^$', counsel_page, name='counsel_page'),
)