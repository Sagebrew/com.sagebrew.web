import pytz
import markdown
from uuid import uuid1
from datetime import datetime
from django.core.urlresolvers import reverse

from neomodel import (StringProperty, RelationshipTo, BooleanProperty,
                      CypherException)

from sb_base.decorators import apply_defense


from sb_base.neo_models import SBVersioned


class Solution(SBVersioned):
    object_type = "02241aee-644f-11e4-9ad9-080027242395"
    table = 'public_solutions'
    action_name = "offered a solution to a question"
    sb_name = "solution"
    up_vote_adjustment = 10
    down_vote_adjustment = 10
    down_vote_cost = 2
    added_to_search_index = BooleanProperty(default=False)
    search_id = StringProperty()

    # relationships
    auto_tags = RelationshipTo('sb_tag.neo_models.AutoTag',
                               'AUTO_TAGGED_AS')
    solution_to = RelationshipTo('sb_questions.neo_models.Question',
                                 'POSSIBLE_ANSWER_TO')

    def get_url(self):
        return reverse("question_detail_page",
                       kwargs={
                           "question_uuid":
                               self.solution_to.all()[0].object_uuid})

    def create_notification(self, pleb, sb_object=None):
        return {
            "profile_pic": pleb.profile_pic,
            "full_name": pleb.get_full_name(),
            "action_name": self.action_name,
            "url": self.get_url()
        }

    @apply_defense
    def create_relations(self, pleb, question=None, wall=None):
        if question is None:
            return False
        try:
            self.solution_to.connect(question)
            question.solutions.connect(self)
            question.solution_count += 1
            question.save()
            rel_from_pleb = pleb.solutions.connect(self)
            rel_from_pleb.save()
            rel_to_pleb = self.owned_by.connect(pleb)
            rel_to_pleb.save()
            self.save()
            return True
        except CypherException as e:
            return e

    @apply_defense
    def edit_content(self, content, pleb):
        try:
            edit_solution = Solution(object_uuid=str(uuid1()), original=False,
                                       content=content).save()
            self.edits.connect(edit_solution)
            edit_solution.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_solution
        except CypherException as e:
            return e

    @apply_defense
    def get_single_dict(self):
        try:
            comment_array = []
            solution_owner = self.owned_by.all()[0]
            for comment in self.comments.all():
                comment_array.append(comment.get_single_dict())
            try:
                parent_object = self.solution_to.all()[0].object_uuid
            except IndexError:
                parent_object = ''
            try:
                if self.content is None:
                    html_content = ""
                else:
                    html_content = markdown.markdown(self.content)
            except AttributeError:
                html_content = ""
            solution_dict = {
                'content': self.content,
                'parent_object': parent_object,
                'object_uuid': self.object_uuid,
                'last_edited_on': unicode(self.last_edited_on),
                'upvotes': self.get_upvote_count(),
                'downvotes': self.get_downvote_count(),
                'vote_count': self.get_vote_count(),
                'owner': solution_owner.username,
                'owner_full_name': "%s %s" % (
                    solution_owner.first_name, solution_owner.last_name),
                'created': unicode(self.created),
                'comments': comment_array,
                'edits': [],
                'object_type': self.object_type,
                'html_content': html_content
            }
            return solution_dict
        except CypherException as e:
            return e
