from django.conf.urls import patterns, url, include

from rest_framework import routers

from sb_quests.endpoints import (PositionViewSet, QuestViewSet)

router = routers.SimpleRouter()

router.register(r'positions', PositionViewSet, base_name='position')
router.register(r'quests', QuestViewSet, base_name='quest')

urlpatterns = patterns(
    'sb_quests.endpoints',
    url(r'^', include(router.urls)),
    (r'^quests/', include('sb_updates.apis.relations.v1')),
    (r'^quests/', include('sb_donations.apis.relations.v1'))
)
