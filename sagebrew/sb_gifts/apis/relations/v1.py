from django.conf.urls import url

from sagebrew.sb_gifts.endpoints import GiftListViewSet


urlpatterns = [
    url(r'^(?P<object_uuid>[A-Za-z0-9.@_%+-]{36})/giftlist/$',
        GiftListViewSet.as_view(), name='mission-giftlist'),
]
