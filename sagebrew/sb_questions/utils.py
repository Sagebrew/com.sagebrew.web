from datetime import datetime
from django.template.loader import render_to_string
from django.core.cache import cache

from neomodel import DoesNotExist, CypherException

from sb_base.decorators import apply_defense

from .serializers import QuestionSerializerNeo
from .neo_models import Question


@apply_defense
def prepare_question_search_html(question_uuid):
    question = cache.get(question_uuid)
    if question is None:
        try:
            question = Question.nodes.get(object_uuid=question_uuid)
        except(Question.DoesNotExist, DoesNotExist):
            return False
        except(CypherException, IOError):
            return None
        cache.set(question_uuid, question)

    owner = question.owned_by.all()[0]
    question_dict = QuestionSerializerNeo(question).data
    question_dict['first_name'] = owner.first_name
    question_dict['last_name'] = owner.last_name
    question_dict['created'] = datetime.strptime(question_dict['created'],
                                                 "%Y-%m-%dT%H:%M:%S.%fZ")
    question_dict['last_edited_on'] = datetime.strptime(
        question_dict['last_edited_on'], "%Y-%m-%dT%H:%M:%S.%fZ")
    rendered = render_to_string('conversation_block.html', question_dict)

    return rendered
