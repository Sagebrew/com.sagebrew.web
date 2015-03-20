import pytz
from datetime import datetime
from django.core.urlresolvers import reverse

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, CypherException)

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
    created_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    up_vote_number = IntegerProperty(default=0)
    down_vote_number = IntegerProperty(default=0)
    view_count = IntegerProperty(default=0)

    # relationships
    is_owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY',
                                 model=CommentedOnRel)
    shared_by = RelationshipTo('plebs.neo_models.Pleb', 'SHARED_BY',
                               model=CommentedOnRel)
    shared_with = RelationshipTo('plebs.neo_models.Pleb', 'SHARED_WITH',
                                 model=CommentedOnRel)
    #TODO Implement the user_referenced, post_referenced, etc. relationships
    #TODO Implement referenced_by_users, referenced_by_post, etc. relationships

    def get_url(self):
        try:
            return reverse("question_detail_page",
                           kwargs={"question_uuid": self.solution_to.all()[
                               0].sb_id})
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
    def get_single_dict(self, pleb=None):
        try:
            try:
                comment_owner = self.is_owned_by.all()[0]
            except IndexError:
                comment_owner = ""
            comment_dict = {'content': self.content,
                            'up_vote_number': self.get_upvote_count(),
                            'object_vote_count': self.get_vote_count(),
                            'object_uuid': self.sb_id,
                            'down_vote_number':
                                self.get_downvote_count(),
                            'last_edited_on':
                                str(self.last_edited_on),
                            'comment_owner': comment_owner.first_name + ' '
                                             + comment_owner.last_name,
                            'comment_owner_email': comment_owner.email,
                            'owner_username': comment_owner.username,
                            'current_user': pleb,
                            'datetime': unicode(self.date_created),
                            'edits': [],
                            'object_type': self.object_type}
            self.view_count += 1
            self.save()
            return comment_dict
        except CypherException as e:
            return e