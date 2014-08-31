import traceback
from django.conf import settings
from elasticsearch import Elasticsearch, helpers

from .neo_models import SBAutoTag, SBTag
from sb_questions.neo_models import SBQuestion

def create_tag_relations(tags):
    '''
    This function creates and manages the relationships between tags, such as
    the frequently_tagged_with relationship.

    :param tags:
    :return:
    '''
    try:
        for tag in tags:
            temp_list = tags
            temp_list.remove(tag)
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


def add_auto_tags_util(tag_list):
    '''
    This function connects the tags generated from alchemyapi to the object
    they were generated from

    :param tag_list:
    :return:
    '''
    tag_array = []
    for tag in tag_list:
        if tag['object_type'] == 'question':
            try:
                question = SBQuestion.index.get(question_id=
                                                tag['object_uuid'])
                relevance = tag['tags']['relevance']
                tag = SBAutoTag.index.get(tag_name=tag['tags']['text'])
                rel = question.auto_tags.connect(tag)
                rel.relevance = relevance
                rel.save()
                tag.questions.connect(question)
                tag_array.append(tag)
            except SBAutoTag.DoesNotExist:
                question =SBQuestion.index.get(question_id=tag['object_uuid'])
                relevance = tag['tags']['relevance']
                tag = SBAutoTag(tag_name=tag['tags']['text'])
                tag.save()
                rel = question.auto_tags.connect(tag)
                rel.relevance = relevance
                rel.save()
                tag.questions.connect(question)
                tag_array.append(tag)
            except SBQuestion.DoesNotExist:
                return False

    create_tag_relations(tag_array)
    return True

def add_tag_util(object_type, object_uuid, tags):
    '''
    This function creates and attaches the tags passed to it to the object
    passed to it

    :param object_type:
    :param object_uuid:
    :param tags:
    :return:
    '''
    tag_array = []
    es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)

    for tag in tags:
        try:
            tag_object = SBTag.index.get(tag_name=tag)
            tag_array.append(tag_object)
        except SBTag.DoesNotExist:
            es.index(index='full-search-base', doc_type='tag',
                     body={'tag_name': tag})
            tag_object = SBTag(tag_name=tag).save()
            tag_array.append(tag_object)

    if object_type == 'question':
        try:
            question = SBQuestion.index.get(question_id=object_uuid)
            for tag in tag_array:
                question.tags.connect(tag)
                tag.questions.connect(question)
                tag.tag_used += 1
                tag.save()
            return True
        except SBQuestion.DoesNotExist:
            return False

