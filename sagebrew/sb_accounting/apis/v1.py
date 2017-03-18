from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_accounting.endpoints import AccountingViewSet


router = routers.SimpleRouter()
router.register(r'accounting', AccountingViewSet, base_name='accounting')

urlpatterns = [
    url(r'^', include(router.urls)),
]
