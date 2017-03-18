from django.conf.urls import url, include

from rest_framework import routers

from sagebrew.sb_quests.endpoints import (PositionViewSet, QuestViewSet)

router = routers.SimpleRouter()

router.register(r'positions', PositionViewSet, base_name='position')
router.register(r'quests', QuestViewSet, base_name='quest')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^quests/', include('sagebrew.sb_updates.apis.relations.v1')),
    url(r'^quests/', include('sagebrew.sb_donations.apis.relations.v1'))
]
