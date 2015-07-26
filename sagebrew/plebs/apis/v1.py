from django.conf.urls import patterns, url, include

from rest_framework import routers

from plebs.endpoints import (UserViewSet, ProfileViewSet, AddressViewSet,
                             FriendRequestViewSet, MeViewSet,
                             FriendManager, FriendRequestList)
from sb_posts.endpoints import (WallPostsListCreate,
                                WallPostsRetrieveUpdateDestroy, post_renderer)

router = routers.SimpleRouter()
me_router = routers.SimpleRouter()
# We could potentially make these nested but currently separated
# as specific actions may be associated with a profile that will
# also require nesting. We will also have alternative types of users
# that may need additional endpoints
router.register(r'users', UserViewSet, base_name="user")
router.register(r'profiles', ProfileViewSet, base_name="profile")
router.register(r'addresses', AddressViewSet, base_name="address")
router.register(r'friend_requests', FriendRequestViewSet,
                base_name="friend_request")
router.register(r'me', MeViewSet, base_name="me")

me_router.register(r'friend_requests', FriendRequestList,
                   base_name="friend_request")


urlpatterns = patterns(
    'plebs.endpoints',
    url(r'^me/', include('sb_notifications.apis.relations.v1')),
    url(r'^me/', include(me_router.urls)),
    url(r'^me/friends/(?P<friend_username>[A-Za-z0-9.@_%+-]{2,30})/$',
        FriendManager.as_view(), name="friend-detail"),
    url(r'^', include(router.urls)),
    url(r'^profiles/(?P<username>[A-Za-z0-9.@_%+-]{2,30})/wall/$',
        WallPostsListCreate.as_view(), name="profile-wall"),
    url(r'^profiles/(?P<username>[A-Za-z0-9.@_%+-]{2,30})/'
        r'wall/render/$',
        post_renderer, name="profile-wall-render"),
    url(r'^profiles/(?P<username>[A-Za-z0-9.@_%+-]{2,30})/wall/'
        r'(?P<post_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        WallPostsRetrieveUpdateDestroy.as_view(),
        name="profile-post")
)
