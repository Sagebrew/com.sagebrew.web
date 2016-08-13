from django.conf.urls import patterns, url

from sb_gifts.endpoints import GiftListViewSet


urlpatterns = patterns(
    'sb_gifts.endpoints',
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/giftlist/$',
        GiftListViewSet.as_view(), name='mission-giftlist'),
)
