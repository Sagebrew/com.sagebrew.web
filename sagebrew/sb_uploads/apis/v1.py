from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_uploads.endpoints import UploadViewSet

router = routers.SimpleRouter()

router.register(r'upload', UploadViewSet, base_name="upload")

urlpatterns = patterns(
    'sb_uploads.endpoints',
    url(r'^', include(router.urls))
)