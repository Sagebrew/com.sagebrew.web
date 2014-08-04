from django.conf.urls import patterns, url

from .views import profile_page


urlpatterns = patterns(
    'plebs.views',
    url(r'^(?P<pleb_email>[A-Za-z0-9.@_%+-]{1,32})/',
       profile_page, name="profile_page")
)