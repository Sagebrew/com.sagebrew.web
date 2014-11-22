from neomodel import CypherException, DoesNotExist

from sb_base.decorators import apply_defense

from .neo_models import SBAnswer

@apply_defense
def save_answer_util(content, answer_uuid):
    '''
    This util creates an answer and saves it, it then connects it to the
    question, and pleb

    :param content:
    :param current_pleb:
    :param answer_uuid:
    :param question_uuid:
    :return:
    '''
    try:
        answer = SBAnswer.nodes.get(sb_id=answer_uuid)
    except (SBAnswer.DoesNotExist, DoesNotExist):
        try:
            answer = SBAnswer(content=content, sb_id=answer_uuid)
            answer.save()
        except CypherException as e:
            return e
    except CypherException as e:
        return e
    return answer

