from django.conf.urls import patterns, url

from sb_donations.endpoints import DonationListCreate


urlpatterns = patterns(
    'sb_flags.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36,36})/donations/$',
        DonationListCreate.as_view(), name='campaign-donations'),
)
