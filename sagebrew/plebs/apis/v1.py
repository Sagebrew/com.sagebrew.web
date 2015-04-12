from django.conf.urls import patterns, url, include

from rest_framework import routers

from plebs.endpoints import UserViewSet, ProfileViewSet, AddressViewSet
from sb_posts.endpoints import (WallPostsListCreate,
                                WallPostsRetrieveUpdateDestroy, post_renderer)

router = routers.SimpleRouter()

# We could potentially make these nested but currently separated
# as specific actions may be associated with a profile that will
# also require nesting. We will also have alternative types of users
# that may need additional endpoints
router.register(r'users', UserViewSet, base_name="user")
router.register(r'profiles', ProfileViewSet, base_name="profile")
router.register(r'addresses', AddressViewSet, base_name="address")

urlpatterns = patterns(
    'plebs.endpoints',
    url(r'^', include(router.urls)),
    url(r'^profiles/(?P<username>[A-Za-z0-9.@_%+-]{1,30})/wall/$',
        WallPostsListCreate.as_view(), name="profile-wall"),
    url(r'^profiles/(?P<username>[A-Za-z0-9.@_%+-]{1,30})/'
        r'wall/render/$',
        post_renderer, name="profile-wall-html"),
    url(r'^profiles/(?P<username>[A-Za-z0-9.@_%+-]{1,30})/wall/'
        r'(?P<post_uuid>[A-Za-z0-9.@_%+-]{36,36})/$',
        WallPostsRetrieveUpdateDestroy.as_view(),
        name="profile-post"),
)