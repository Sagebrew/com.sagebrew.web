from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_accounting.endpoints import AccountingViewSet


router = routers.SimpleRouter()
router.register(r'accounting', AccountingViewSet, base_name='accounting')

urlpatterns = patterns(
    'sb_accounting.endpoints',
    url(r'^', include(router.urls)),
)
