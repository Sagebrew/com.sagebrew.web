import pytz
from uuid import uuid1
from datetime import datetime

from api.utils import spawn_task
from plebs.neo_models import Pleb
from .neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion

def save_answer_util(content="", current_pleb="", answer_uuid="",
                     question_uuid=""):
    '''
    This util creates an answer and saves it, it then connects it to the question,
    and pleb

    :param content:
    :param current_pleb:
    :param answer_uuid:
    :param question_uuid:
    :return:
    '''
    try:
        my_pleb = Pleb.index.get(email=current_pleb)
        question = SBQuestion.index.get(question_id=question_uuid)
        answer = SBAnswer(content=content, answer_id=answer_uuid)
        answer.save()
        answer.answer_to.connect(question)
        question.answer.connect(answer)
        rel_from_pleb = my_pleb.answers.connect(answer)
        rel_from_pleb.save()
        rel_to_pleb = answer.owned_by.connect(my_pleb)
        rel_to_pleb.save()
        answer.save()
        return True
    except Pleb.DoesNotExist, SBQuestion.DoesNotExist:
        return False
    except Exception, e:
        print e
        return False

def edit_answer_util(content="", current_pleb="", answer_uuid=""):
    pass

def upvote_answer_util(current_pleb=""):
    pass

def downvote_answer_util(current_pleb=""):
    pass

