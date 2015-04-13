import pytz
import markdown
from uuid import uuid1
from datetime import datetime

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,  BooleanProperty, FloatProperty,
                      CypherException)
from neomodel import db

from api.utils import execute_cypher_query
from sb_base.neo_models import SBPublicContent
from sb_tag.neo_models import Tag

from sb_base.decorators import apply_defense


class Question(SBPublicContent):
    table = 'public_questions'
    action_name = "asked a question"
    up_vote_adjustment = 5
    down_vote_adjustment = 2
    object_type = "0274a216-644f-11e4-9ad9-080027242395"
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
        queryset = [Tag.inflate(row[0]).tag_name for row in res]
        return queryset

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
    def delete_content(self, pleb):
        try:
            self.content = ""
            self.title = ""
            self.to_be_deleted = True
            self.save()
            return self
        except CypherException as e:
            return e

    @apply_defense
    def get_single_dict(self):
        from sb_solutions.neo_models import Solution
        try:
            solution_array = []
            comment_array = []
            owner = self.owned_by.all()
            try:
                owner = owner[0]
            except IndexError as e:
                return e
            # TODO is this used for storing solutions and comments
            # into dynamo? Or can we get rid of it and just return
            # the question specific data?
            query = 'match (q:Question) where q.object_uuid="%s" ' \
                    'with q ' \
                    'match (q)-[:POSSIBLE_ANSWER]-(a:Solution) ' \
                    'where a.to_be_deleted=False ' \
                    'return a ' % self.object_uuid
            solutions, meta = execute_cypher_query(query)
            solutions = [Solution.inflate(row[0]) for row in solutions]
            for solution in solutions:
                solution_array.append(solution.get_single_dict())
            edit = self.get_most_recent_edit()
            for comment in self.comments.all():
                comment_array.append(comment.get_single_dict())
            if self.content is None:
                html_content = ""
            else:
                html_content = markdown.markdown(self.content)
            # TODO this should be replaced with the serializer
            return {
                'title': edit.title,
                'content': edit.content,
                'object_uuid': self.object_uuid,
                'is_closed': self.is_closed,
                'solution_count': self.solution_count,
                'last_edited_on': unicode(self.last_edited_on),
                'upvotes': self.get_upvote_count(),
                'downvotes': self.get_downvote_count(),
                'vote_count': self.get_vote_count(),
                'owner': owner.username,
                'owner_full_name': "%s %s" % (
                    owner.first_name, owner.last_name),
                'created': unicode(self.created),
                'solutions': solution_array,
                'comments': comment_array,
                'edits': [],
                'object_type': self.object_type,
                'to_be_deleted': self.to_be_deleted,
                'html_content': html_content}
        except (CypherException, IOError) as e:
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