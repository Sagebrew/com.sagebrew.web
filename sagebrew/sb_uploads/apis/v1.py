from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_uploads.endpoints import UploadViewSet, URLContentViewSet

router = routers.SimpleRouter()

router.register(r'upload', UploadViewSet, base_name="upload")
router.register(r'urlcontent', URLContentViewSet, base_name="urlcontent")

urlpatterns = [
    url(r'^', include(router.urls))
]
