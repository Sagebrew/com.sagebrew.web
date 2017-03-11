from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_orders.endpoints import OrderViewSet


router = routers.SimpleRouter()
router.register(r'orders', OrderViewSet, base_name='orders')

urlpatterns = [
    url(r'^', include(router.urls)),
]
