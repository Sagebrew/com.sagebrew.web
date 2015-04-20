from django.template.loader import render_to_string

from neomodel import DoesNotExist

from sb_base.decorators import apply_defense

from .serializers import QuestionSerializerNeo
from .neo_models import Question


@apply_defense
def prepare_question_search_html(question_uuid, request):
    try:
        question = Question.nodes.get(object_uuid=question_uuid)
    except (Question.DoesNotExist, DoesNotExist):
        return False

    owner = question.owned_by.all()[0]
    question_dict = QuestionSerializerNeo(
        question, context={"request": request}).data
    question_dict['first_name'] = owner.first_name
    question_dict['last_name'] = owner.last_name
    rendered = render_to_string('conversation_block.html', question_dict)

    return rendered
