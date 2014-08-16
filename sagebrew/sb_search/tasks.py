from uuid import uuid1
from traceback import print_exc
from django.conf import settings

from celery import shared_task

from plebs.neo_models import Pleb
from sb_posts.neo_models import SBPost
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion


@shared_task()
def update_weight_relationship(object_type="", object_uuid=str(uuid1()),
                               current_pleb="", modifier_type=""):
    '''
    This task handles creating and updating the weight relationship between
    users and: other users, questions, answers and posts. These relationships
    are used in generating more personalized search results via the
    point system

    :param object_type:
    :param object_uuid:
    :param current_pleb:
    :param modifier_type:
    :return:
    '''
    try:
        if object_type == 'question':
            question = SBQuestion.index.get(question_id=object_uuid)
            pleb = Pleb.index.get(email=current_pleb)
            if pleb.object_weight.is_connected(question):
                rel = pleb.object_weight.relationship(question)
                if rel.seen and modifier_type == 'seen':
                    rel.weight += settings.USER_RELATIONSHIP_MODIFIER['each_seen']
                    rel.save()
                    return True
                if modifier_type == 'comment_on':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS['comment_on']
                    rel.status = 'commented_on'
                    rel.save()
                if modifier_type == 'flag_as_inappropriate':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS['flag_as_inappropriate']
                    rel.status = 'flagged_as_inappropriate'
                    rel.save()
                if modifier_type == 'flag_as_spam':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS['flag_as_spam']
                    rel.status = 'flagged_as_spam'
                    rel.save()
                if modifier_type == 'share':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS['share']
                    rel.status = 'shared'
                    rel.save()
                if modifier_type == 'answered':
                    rel.weight += settings.OBJECT_SEARCH_MODIFIERS['answered']
                    rel.status = 'answered'
                    rel.save()
            else:
                rel = pleb.object_weight.connect(question)
                rel.save()
                return True

        if object_type == 'pleb':
            pleb = Pleb.index.get(email=object_uuid)
        if object_type == 'post':
            post = SBPost.index.get(post_id=object_uuid)
        if object_type == 'answer':
            answer = SBAnswer.index.get(answer_id = object_uuid)
    except Exception, e:
        print_exc()
        return False
