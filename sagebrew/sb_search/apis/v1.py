from django.conf.urls import patterns, url

from sb_search.endpoints import SearchViewSet, AmazonProductSearchViewSet

urlpatterns = patterns(
    'sb_search.endpoints',
    url(r'^search/', SearchViewSet.as_view(), name="search-list"),
    url(r'^product_search/', AmazonProductSearchViewSet.as_view(),
        name="product-search-list")
)
