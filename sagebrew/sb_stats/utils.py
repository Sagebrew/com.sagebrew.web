from logging import getLogger

from django.core.cache import cache

from neomodel import CypherException, db

from sb_base.neo_models import VotableContent
from sb_questions.neo_models import Question

logger = getLogger('loggly_logs')


def update_view_count(object_uuid):
    try:
        query = 'MATCH (a:VotableContent {object_uuid: "%s"}) ' \
                'RETURN a' % (object_uuid)
        res, col = db.cypher_query(query)

        sb_object = VotableContent.inflate(res[0][0])
        sb_object.increment_view_count()
        child_class = sb_object.get_child_label()
        logger.critical(child_class)
        if "Question" in child_class:
            question = Question.inflate(res[0][0])
            cache.set(question.object_uuid, question)
    except(CypherException, IOError) as e:
        return e

    return sb_object
