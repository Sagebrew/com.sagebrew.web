from django.conf.urls import url

from .views import search_result_view

urlpatterns = [
    url(r'^$', search_result_view, name="search_results"),
]
