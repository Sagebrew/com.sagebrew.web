import pytz
from uuid import uuid1
from datetime import datetime

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,  BooleanProperty, FloatProperty,
                      CypherException)
from neomodel import db

from sb_base.neo_models import SBPublicContent
from sb_tag.neo_models import Tag

from sb_base.decorators import apply_defense
from sb_solutions.neo_models import Solution


class Question(SBPublicContent):
    table = 'public_questions'
    action_name = "asked a question"
    up_vote_adjustment = 5
    down_vote_adjustment = 2
    # This currently isn't maintained please make sure to use the methods
    # provided in the serializer or in the endpoint
    #  /v1/questions/uuid/solution_count/
    solution_count = IntegerProperty(default=0)
    title = StringProperty()
    is_closed = BooleanProperty(default=False)
    is_private = BooleanProperty()
    is_protected = BooleanProperty(default=False)
    is_mature = BooleanProperty(default=False)
    positivity = FloatProperty()
    subjectivity = FloatProperty()
    title_polarity = FloatProperty()
    title_subjectivity = FloatProperty()
    search_id = StringProperty()
    tags_added = BooleanProperty(default=False)

    # relationships
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    solutions = RelationshipTo('sb_solutions.neo_models.Solution',
                               'POSSIBLE_ANSWER')

    def get_tags(self):
        query = "MATCH (a:Question {object_uuid:'%s'})-[:TAGGED_AS]->" \
                "(b:Tag) RETURN b" % (self.object_uuid)
        res, col = db.cypher_query(query)
        queryset = [Tag.inflate(row[0]).name for row in res]
        return queryset

    def get_solutions(self):
        query = 'MATCH (a:Question)-->(solutions:Solution) ' \
            'WHERE (a.object_uuid = "%s" and ' \
            'solutions.to_be_deleted = false)' \
            'RETURN solutions' % (self.object_uuid)
        res, col = db.cypher_query(query)
        return [Solution.inflate(row[0]) for row in res]

    def get_solution_ids(self):
        query = 'MATCH (a:Question)-->(solutions:Solution) ' \
            'WHERE (a.object_uuid = "%s" and ' \
            'solutions.to_be_deleted = false)' \
            'RETURN solutions.object_uuid' % (self.object_uuid)

        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    @apply_defense
    def edit_content(self, pleb, content):
        from sb_questions.utils import create_question_util
        try:
            edit_question = create_question_util(content, self.title,
                                                 str(uuid1()))

            if isinstance(edit_question, Exception) is True:
                return edit_question

            edit_question.original = False
            edit_question.save()
            self.edits.connect(edit_question)
            edit_question.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_question
        except (CypherException, AttributeError) as e:
            return e

    @apply_defense
    def edit_title(self, title):
        from sb_questions.utils import create_question_util
        try:
            edit_question = create_question_util(self.content, title,
                                                 str(uuid1()))

            if isinstance(edit_question, Exception) is True:
                return edit_question
            edit_question.original = False
            edit_question.save()
            self.edits.connect(edit_question)
            edit_question.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_question
        except CypherException as e:
            return e

    @apply_defense
    def get_original(self):
        try:
            if self.original is True:
                return self
            return self.edit_to.all()[0]
        except CypherException as e:
            return e

    @apply_defense
    def get_most_recent_edit(self):
        try:
            results, columns = self.cypher('start q=node({self}) '
                                           'match q-[:EDIT]-(n:Question) '
                                           'with n '
                                           'ORDER BY n.created DESC'
                                           ' return n')
            edits = [self.inflate(row[0]) for row in results]
            if not edits:
                return self
            return edits[0]
        except CypherException as e:
            return e