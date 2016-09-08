from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_orders.endpoints import OrderViewSet


router = routers.SimpleRouter()
router.register(r'orders', OrderViewSet, base_name='orders')

urlpatterns = patterns(
    'sb_orders.endpoints',
    url(r'^', include(router.urls)),

)
