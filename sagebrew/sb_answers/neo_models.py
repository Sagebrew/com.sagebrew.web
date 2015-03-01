import pytz
import markdown
from uuid import uuid1
from datetime import datetime
from django.core.urlresolvers import reverse

from neomodel import (StringProperty, RelationshipTo, BooleanProperty,
                      CypherException)

from sb_base.decorators import apply_defense


from sb_base.neo_models import SBVersioned


class SBAnswer(SBVersioned):
    object_type = "02241aee-644f-11e4-9ad9-080027242395"
    table = 'public_solutions'
    action = "offered a solution to a question"
    up_vote_adjustment = 10
    down_vote_adjustment = 10
    down_vote_cost = 2
    sb_name = "answer"
    added_to_search_index = BooleanProperty(default=False)
    search_id = StringProperty()

    # relationships
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS')
    answer_to = RelationshipTo('sb_questions.neo_models.SBQuestion',
                               'POSSIBLE_ANSWER_TO')

    def get_url(self):
        return reverse("question_detail_page",
                       kwargs={"question_uuid": self.answer_to.all()[0].sb_id})

    def create_notification(self, pleb, sb_object=None):
        return {
            "profile_pic": pleb.profile_pic,
            "full_name": pleb.get_full_name(),
            "action": self.action,
            "url": self.get_url()
        }

    @apply_defense
    def create_relations(self, pleb, question=None, wall=None):
        if question is None:
            return False
        try:
            self.answer_to.connect(question)
            question.answer.connect(self)
            question.answer_number += 1
            question.save()
            rel_from_pleb = pleb.answers.connect(self)
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
            edit_answer = SBAnswer(sb_id=str(uuid1()), original=False,
                                   content=content).save()
            self.edits.connect(edit_answer)
            edit_answer.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_answer
        except CypherException as e:
            return e

    @apply_defense
    def get_single_dict(self, pleb=None):
        try:
            comment_array = []
            answer_owner = self.owned_by.all()[0]
            answer_owner_name = answer_owner.first_name +' '+answer_owner.last_name
            answer_owner_url = answer_owner.username
            for comment in self.comments.all():
                comment_array.append(comment.get_single_dict())
            try:
                parent_object = self.answer_to.all()[0].sb_id
            except IndexError:
                parent_object = ''
            answer_dict = {'content': self.content,
                           'current_pleb': pleb,
                           'parent_object': parent_object,
                           'object_uuid': self.sb_id,
                           'last_edited_on': unicode(self.last_edited_on),
                           'up_vote_number': self.get_upvote_count(),
                           'down_vote_number': self.get_downvote_count(),
                           'vote_score': self.get_vote_count(),
                           'answer_owner_name': answer_owner_name,
                           'answer_owner_url': answer_owner.username,
                           'time_created': unicode(self.date_created),
                           'comments': comment_array,
                           'answer_owner_email': answer_owner.email,
                           'edits': [],
                           'object_type': self.object_type,
                           'html_content': markdown.markdown(self.content)}
            return answer_dict
        except CypherException as e:
            return e


