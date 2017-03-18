from django.conf.urls import url

from sagebrew.sb_donations.endpoints import DonationListCreate


urlpatterns = [
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{2,36})/donations/$',
        DonationListCreate.as_view(), name='campaign-donations'),
]
