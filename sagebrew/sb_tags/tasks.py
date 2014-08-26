from celery import shared_task

from sb_questions.neo_models import SBQuestion
from sb_answers.neo_models import SBAnswer
from sb_posts.neo_models import SBPost
from sb_tags.neo_models import SBAutoTag

@shared_task()
def add_auto_tags(tag, object_uuid, object_type):
    if object_type == 'question':
        try:
            question = SBQuestion.index.get(question_id=object_uuid)
            tag = SBAutoTag.index.get(tag_name=tag['text'])
            question.auto_tags.connect(tag)
            tag.questions.connect(question)
            return True
        except SBAutoTag.DoesNotExist:
            question =SBQuestion.index.get(question_id=object_uuid)
            tag = SBAutoTag(tag_name=tag['text'])
            tag.save()
            question.auto_tags.connect(tag)
            tag.questions.connect(question)
            return True
        except SBQuestion.DoesNotExist:
            return False