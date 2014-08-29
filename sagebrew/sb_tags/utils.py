import traceback

from .neo_models import SBAutoTag
from sb_questions.neo_models import SBQuestion

def create_tag_relations(tags):
    try:
        for tag in tags:
            temp_list = tags.pop(tag)
            print temp_list
            print tags
            for item in temp_list:
                if tag.frequently_auto_tagged_with.is_connected(item):
                    rel = tag.frequently_auto_tagged_with.relationship(item)
                    rel.count += 1
                    rel.save()
                else:
                    rel = tag.frequently_auto_tagged_with.connect(item)
                    rel.save()
            temp_list = []
        return True
    except Exception:
        traceback.print_exc()
        return False


def add_auto_tags_util(tag):
    tag_array = []
    if tag['object_type'] == 'question':
        try:
            question = SBQuestion.index.get(question_id=
                                            tag['object_uuid'])
            tag = SBAutoTag.index.get(tag_name=tag['text'])
            question.auto_tags.connect(tag)
            tag.questions.connect(question)
            tag_array.append(tag)
            return True
        except SBAutoTag.DoesNotExist:
            question =SBQuestion.index.get(question_id=tag['object_uuid'])
            tag = SBAutoTag(tag_name=tag['text'])
            tag.save()
            question.auto_tags.connect(tag)
            tag.questions.connect(question)
            tag_array.append(tag)
            return True
        except SBQuestion.DoesNotExist:
            return False
    create_tag_relations(tag_array)