from django.core.cache import cache
from django.utils.text import slugify

from rest_framework.reverse import reverse

from py2neo.cypher.error.transaction import CouldNotCommit, ClientError
from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo, BooleanProperty, FloatProperty,
                      db, DoesNotExist, CypherException)

from sb_base.neo_models import TitledContent

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
    is_private = BooleanProperty()
    is_protected = BooleanProperty(default=False)
    is_mature = BooleanProperty(default=False)
    positivity = FloatProperty()
    subjectivity = FloatProperty()
    title_polarity = FloatProperty()
    title_subjectivity = FloatProperty()
    tags_added = BooleanProperty(default=False)
    title = StringProperty(unique_index=True)

    # optimizations
    longitude = FloatProperty()
    latitude = FloatProperty()
    affected_area = StringProperty()
    # Google place_id
    external_location_id = StringProperty(index=True)

    # relationships

    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    solutions = RelationshipTo('sb_solutions.neo_models.Solution',
                               'POSSIBLE_ANSWER')
    focus_location = RelationshipTo('sb_locations.neo_models.Location',
                                    'FOCUSED_ON')

    @classmethod
    def get(cls, object_uuid):
        question = cache.get(object_uuid)
        if question is None:
            res, _ = db.cypher_query(
                "MATCH (a:%s {object_uuid:'%s'}) RETURN a" % (
                    cls.__name__, object_uuid))
            try:
                res[0][0].pull()
                question = cls.inflate(res[0][0])
            except IndexError:
                raise DoesNotExist('Question with id: %s '
                                   'does not exist' % object_uuid)
            cache.set(object_uuid, question)
        return question

    def get_tags(self):
        query = "MATCH (a:Question {object_uuid:'%s'})-[:TAGGED_AS]->" \
                "(b:Tag) RETURN b.name" % self.object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    def get_tags_humanized(self):
        return [tag.replace('-', ' ').replace('_', ' ')
                for tag in self.get_tags()]

    def get_tags_string(self):
        try:
            return ", ".join(self.get_tags())
        except (CypherException, IOError, CouldNotCommit, ClientError):
            return ""

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

    def get_conversation_authors(self):
        from plebs.neo_models import Pleb
        query = 'MATCH (a:Question {object_uuid: "%s"}) WITH a ' \
                'OPTIONAL MATCH (a)-[:POSSIBLE_ANSWER]->(solutions:Solution) ' \
                'WHERE solutions.to_be_deleted = false ' \
                'RETURN collect(a.owner_username) + ' \
                'collect(solutions.owner_username) as authors' % (
                    self.object_uuid)
        res, _ = db.cypher_query(query)
        authors = list(set(res.one))
        author_list = []
        for author in authors:
            pleb = Pleb.get(author)
            author_list.append("%s %s" % (pleb.first_name, pleb.last_name))
        return ", ".join(author_list[::-1])

    def get_url(self, request=None):
        return reverse('question_detail_page',
                       kwargs={'question_uuid': self.object_uuid,
                               'slug': slugify(self.title)},
                       request=request)
