from django.conf.urls import url

from sagebrew.sb_search.endpoints import (
    SearchViewSet, AmazonProductSearchViewSet)

urlpatterns = [
    url(r'^search/', SearchViewSet.as_view(), name="search-list"),
    url(r'^product_search/', AmazonProductSearchViewSet.as_view(),
        name="product-search-list")
]
