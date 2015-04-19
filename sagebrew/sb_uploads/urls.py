from django.conf.urls import patterns, url

from .views import upload_image_api, get_image_api


urlpatterns = patterns(
    'sb_uploads.views',
    url(r'^images/$', upload_image_api, name="upload_image_api"),
    url(r'^images/get/', get_image_api, name="get_image_api")
)
