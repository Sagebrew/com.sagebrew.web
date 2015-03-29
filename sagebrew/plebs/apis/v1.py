from django.conf.urls import patterns, url, include

from rest_framework import routers

from plebs.endpoints import UserViewSet, ProfileViewSet

router = routers.SimpleRouter()

# We could potentially make these nested but currently separated
# as specific actions may be associated with a profile that will
# also require nesting. We will also have alternative types of users
# that may need additional endpoints
router.register(r'users', UserViewSet, base_name="user")
router.register(r'profiles', ProfileViewSet, base_name="profile")

urlpatterns = patterns(
    'plebs.views',
    url(r'^', include(router.urls)),
)