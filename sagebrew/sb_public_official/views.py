from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import CypherException
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def get_search_html(request, object_uuid):
    try:
        quest = Quest.get(object_uuid)
    except (CypherException, IOError):
        return Response('Server Error', status=500)
    rendered_html = render_to_string("saga_search_block.html",
                                     QuestSerializer(
                                         quest,
                                         context={'request': request}).data)

    return Response({'html': rendered_html}, status=200)
