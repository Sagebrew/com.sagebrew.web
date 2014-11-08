from django.conf.urls import url, patterns

from .views import delete_object_view

urlpatterns = patterns(
    'sb_deletes.views',
    url(r'^delete_object_api/$', delete_object_view, name="delete_object_view")
)