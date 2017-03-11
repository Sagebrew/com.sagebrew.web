from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_news.endpoints import NewsArticleViewSet


router = routers.SimpleRouter()
router.register(r'news', NewsArticleViewSet, base_name="news")


urlpatterns = [
    url(r'^', include(router.urls)),
]
