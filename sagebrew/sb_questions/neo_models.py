from django.core.cache import cache

from rest_framework.reverse import reverse

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo, BooleanProperty, FloatProperty,
                      db, DoesNotExist)

from sb_base.neo_models import TitledContent
from sb_tags.neo_models import Tag

from sb_solutions.neo_models import Solution


class Question(TitledContent):
    table = StringProperty(default='public_questions')
    action_name = StringProperty(default="asked a question")
    visibility = StringProperty(default="public")
    up_vote_adjustment = IntegerProperty(default=5)
    down_vote_adjustment = IntegerProperty(default=-2)
    # This currently isn't maintained please make sure to use the methods
    # provided in the serializer or in the endpoint
    #  /v1/questions/uuid/solution_count/
    solution_count = IntegerProperty(default=0)
    is_closed = BooleanProperty(default=False)
    is_private = BooleanProperty()
    is_protected = BooleanProperty(default=False)
    is_mature = BooleanProperty(default=False)
    positivity = FloatProperty()
    subjectivity = FloatProperty()
    title_polarity = FloatProperty()
    title_subjectivity = FloatProperty()
    tags_added = BooleanProperty(default=False)

    # relationships
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    solutions = RelationshipTo('sb_solutions.neo_models.Solution',
                               'POSSIBLE_ANSWER')

    @classmethod
    def get(cls, object_uuid):
        question = cache.get(object_uuid)
        if question is None:
            res, _ = db.cypher_query(
                "MATCH (a:%s {object_uuid:'%s'}) RETURN a" % (
                    cls.__name__, object_uuid))
            try:
                question = cls.inflate(res[0][0])
            except IndexError:
                raise DoesNotExist('Question with id: %s '
                                   'does not exist' % object_uuid)
            cache.set(object_uuid, question)
        return question

    def get_tags(self):
        query = "MATCH (a:Question {object_uuid:'%s'})-[:TAGGED_AS]->" \
                "(b:Tag) RETURN b" % self.object_uuid
        res, col = db.cypher_query(query)
        queryset = [Tag.inflate(row[0]).name for row in res]
        return queryset

    def get_solutions(self):
        query = 'MATCH (a:Question {object_uuid: "%s"})-' \
                '[:POSSIBLE_ANSWER]->(solutions:Solution) ' \
                'WHERE solutions.to_be_deleted = false ' \
                'RETURN solutions' % self.object_uuid
        res, col = db.cypher_query(query)
        return [Solution.inflate(row[0]) for row in res]

    def get_solution_ids(self):
        query = 'MATCH (a:Question {object_uuid: "%s"})' \
                '-[:POSSIBLE_ANSWER]->(solutions:Solution) ' \
                'WHERE solutions.to_be_deleted = false ' \
                'RETURN solutions.object_uuid' % self.object_uuid

        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    def get_url(self, request=None):
        return reverse('question_detail_page',
                       kwargs={'question_uuid': self.object_uuid},
                       request=request)
