from logging import getLogger
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from celery import shared_task

from django.core.cache import cache
from django.conf import settings

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task, create_auto_tags
from sb_tags.tasks import add_auto_tags

from .neo_models import Question

logger = getLogger("loggly_logs")


@shared_task()
def create_question_summary_task(object_uuid):
    try:
        question = Question.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Question.DoesNotExist, CypherException, IOError) as e:
        raise add_auto_tags_to_question_task.retry(exc=e, countdown=5,
                                                   max_retries=None)
    language = "english"
    stemmer = Stemmer(language)
    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)
    summary = ""
    sentence_list = [
        unicode(sentence) for sentence in summarizer(
            PlaintextParser.from_string(
                question.content.encode(
                    'utf-8').strip().decode('utf-8'),
                Tokenizer(language)).document,
            settings.DEFAULT_SENTENCE_COUNT)]
    for sentence in sentence_list:
        excluded = [exclude
                    for exclude in settings.DEFAULT_EXCLUDE_SENTENCES
                    if exclude in sentence]
        logger.critical(excluded)
        if settings.TIME_EXCLUSION_REGEX.search(sentence) is None \
                and len(summary) < settings.DEFAULT_SUMMARY_LENGTH \
                and excluded not in sentence:
            summary += " " + sentence
    question.summary = summary
    question.save()
    cache.delete(question.object_uuid)

    return question


@shared_task()
def add_auto_tags_to_question_task(object_uuid):
    '''
    This function will take a question object, a list of
    tags and auto tags and manage the other tasks which attach them to
    the question.

    :param question:
    :return:
    '''
    try:
        question = Question.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, Question.DoesNotExist, CypherException, IOError) as e:
        raise add_auto_tags_to_question_task.retry(exc=e, countdown=5,
                                                   max_retries=None)
    auto_tags = create_auto_tags(question.content)
    if isinstance(auto_tags, Exception) is True:
        raise add_auto_tags_to_question_task.retry(
            exc=auto_tags, countdown=3, max_retries=None)

    task_data = []
    for tag in auto_tags.get('keywords', []):
        task_data.append({"tags": tag})

    auto_tag_data = {
        'question': question,
        'tag_list': task_data
    }
    spawned = spawn_task(task_func=add_auto_tags,
                         task_param=auto_tag_data)
    if isinstance(spawned, Exception) is True:
        raise add_auto_tags_to_question_task.retry(exc=spawned, countdown=3,
                                                   max_retries=None)

    return spawned
