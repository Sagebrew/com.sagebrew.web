import pytz
from datetime import datetime
from django.core.urlresolvers import reverse

from neomodel import (IntegerProperty, DateTimeProperty, RelationshipTo,
                      StructuredRel, CypherException)

from sb_base.decorators import apply_defense
from sb_base.neo_models import SBNonVersioned


class CommentedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class SBComment(SBNonVersioned):
    table = 'comments'
    up_vote_adjustment = 2
    down_vote_adjustment = 1
    action = "commented on your "
    sb_name = "comment"
    object_type = "02ba1c88-644f-11e4-9ad9-080027242395"
    upvotes = IntegerProperty(default=0)
    downvotes = IntegerProperty(default=0)
    view_count = IntegerProperty(default=0)

    def get_url(self):
        try:
            return reverse("question_detail_page",
                           kwargs={"question_uuid": self.solution_to.all()[
                               0].object_uuid})
        except IndexError:
            return False

    def create_notification(self, pleb, sb_object=None):
        return {
            "profile_pic": pleb.profile_pic,
            "full_name": pleb.get_full_name(),
            "action": self.action + sb_object.sb_name,
            "url": self.get_url()
        }

    def comment_on(self, comment):
        pass

    @apply_defense
    def get_single_dict(self):
        try:
            try:
                comment_owner = self.owned_by.all()[0]
            except IndexError:
                comment_owner = ""
            comment_dict = {
                'content': self.content,
                'upvotes': self.get_upvote_count(),
                'vote_count': self.get_vote_count(),
                'object_uuid': self.object_uuid,
                'downvotes':
                    self.get_downvote_count(),
                'last_edited_on':
                    str(self.last_edited_on),
                'comment_owner': comment_owner.first_name + ' '
                                 + comment_owner.last_name,
                'comment_owner_email': comment_owner.email,
                'owner_username': comment_owner.username,
                'owner_full_name': "%s %s" % (
                                comment_owner.first_name,
                                comment_owner.last_name),
                'owner': comment_owner.username,
                'created': unicode(self.created),
                'edits': [],
                'object_type': self.object_type
            }
            self.view_count += 1
            self.save()
            return comment_dict
        except CypherException as e:
            return e