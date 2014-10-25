import logging
from json import dumps
from django.conf import settings
from elasticsearch import Elasticsearch
from neomodel.exception import UniqueProperty, DoesNotExist, CypherException

from .neo_models import SBAutoTag, SBTag
from sb_questions.neo_models import SBQuestion
from sb_answers.neo_models import SBAnswer

logger = logging.getLogger('loggly_logs')


def create_tag_relations(tags):
    '''
    This function creates and manages the relationships between tags, such as
    the frequently_tagged_with relationship.

    :param tags:
    :return:
    '''
    if not tags:
        return False

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
            # TODO is this needed since temp_list is assigned to tags at the
            # start of the for loop?
            temp_list = []
        return True

    except Exception:
        logger.exception(dumps({"function": create_tag_relations.__name__,
                                "exception": "UnhandledException: "}))
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
                try:
                    question = SBQuestion.nodes.get(question_id=
                                                    tag['object_uuid'])
                except (SBQuestion.DoesNotExist, DoesNotExist):
                    return None
                relevance = tag['tags']['relevance']
                tag = SBAutoTag.nodes.get(tag_name=tag['tags']['text'])
                rel = question.auto_tags.connect(tag)
                rel.relevance = relevance
                rel.save()
                tag.questions.connect(question)
                tag_array.append(tag)
            except (SBAutoTag.DoesNotExist, DoesNotExist):
                try:
                    question =SBQuestion.nodes.get(question_id=tag['object_uuid'])
                    relevance = tag['tags']['relevance']
                    tag = SBAutoTag(tag_name=tag['tags']['text'])
                    tag.save()
                    rel = question.auto_tags.connect(tag)
                    rel.relevance = relevance
                    rel.save()
                    tag.questions.connect(question)
                    tag_array.append(tag)
                except UniqueProperty:
                    logger.exception({'function': add_auto_tags_util.__name__,
                                      'exception': "UniqueProperty: "})
                    return None

            except KeyError:
                return False

            except IndexError:
                return False

            except Exception:
                logger.exception({'function': add_auto_tags_util.__name__,
                                  'exception': "UnhandledException: "})
                return None
        else:
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

    if not tags:
        return False

    for tag in tags:
        try:
            tag_object = SBTag.nodes.get(tag_name=tag)
            tag_array.append(tag_object)
        except (SBTag.DoesNotExist, DoesNotExist):
            es.index(index='tags', doc_type='tag',
                     body={'tag_name': tag})
            tag_object = SBTag(tag_name=tag).save()
            tag_array.append(tag_object)

    if object_type == 'question':
        try:
            try:
                question = SBQuestion.nodes.get(question_id=object_uuid)
            except (SBQuestion.DoesNotExist, DoesNotExist):
                return None
            for tag in tag_array:
                question.tags.connect(tag)
                tag.questions.connect(question)
                tag.tag_used += 1
                tag.save()
            return True

        except CypherException:
            return None

        except Exception:
            logger.exception(dumps({"function": add_tag_util.__name__,
                                "exception": "UnhandledException: "}))
            return None
    else:
        return False
