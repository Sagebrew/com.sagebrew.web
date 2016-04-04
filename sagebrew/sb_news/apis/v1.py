from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_news.endpoints import NewsArticleViewSet


router = routers.SimpleRouter()
router.register(r'news', NewsArticleViewSet, base_name="news")


urlpatterns = patterns(
    'sb_news.endpoints',
    url(r'^', include(router.urls)),
)
