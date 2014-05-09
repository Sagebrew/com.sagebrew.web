from django.conf.urls import patterns, url

from .views import (standard_settings, address_settings, user_settings,
                    picture_settings, user_profile, home_profile)


urlpatterns = patterns('user_profiles.views',
    url(r'^settings/$', standard_settings),
    url(r'^settings/standard_settings$', standard_settings),
    url(r'^settings/address_settings$', address_settings),
    url(r'^settings/user_settings$', user_settings),
    url(r'^settings/picture_settings$', picture_settings),
    url(r'^(?P<user_name>[A-Za-z0-9._%+-]{1,32})/$', user_profile,
                                        name='user_profile'),
    url(r'^$', home_profile),
)
