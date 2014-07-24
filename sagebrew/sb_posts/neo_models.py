import pytz

from uuid import uuid1
from datetime import datetime

from random import random
from django.dispatch import receiver
from django.db.models.signals import post_save


from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne)

class PostedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

class PostReceivedRel(StructuredRel):
    received = BooleanProperty()

class SBBase(StructuredNode):
    content = StringProperty()
    date_created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    up_vote_number = IntegerProperty(default=0)
    down_vote_number = IntegerProperty(default=0)
    last_edited_on = DateTimeProperty(default=None)
    to_be_deleted = BooleanProperty(default=False)

    #relationships
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY', model=PostedOnRel)
    up_voted_by = RelationshipTo('plebs.neo_models.Pleb', 'UP_VOTED_BY')
    down_voted_by = RelationshipTo('plebs.neo_models.Pleb', 'DOWN_VOTED_BY')
    flagged_by = RelationshipTo('plebs.neo_models.Pleb', 'FLAGGED_BY')
    received_by = RelationshipTo('plebs.neo_models.Pleb', 'RECEIVED', model=PostReceivedRel)
    comments = RelationshipTo('sb_comments.neo_models.SBComment', 'HAS_A', model=PostedOnRel)

class SBPost(SBBase):
    post_id = StringProperty(unique_index=True)

    #relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.SBWall', 'POSTED_ON')
    #TODO Implement referenced_by_... relationships
    #TODO Implement ..._referenced relationships

class SBQuestion(SBBase):
    question_id = StringProperty()
    has_selected_answer = BooleanProperty(default=False)

    #relationships
    selected_answer = RelationshipTo('SBAnswer', 'SELECTED_ANSWER')
    answer = RelationshipTo('SBAnswer', 'POSSIBLE_ANSWER')


class SBAnswer(SBBase):
    answer_id = StringProperty()
    selected_answer = BooleanProperty(default=False)

    #relationships
    possible_answer_to = RelationshipTo('SBQuestion', 'ANSWER')
    selected_answer_to = RelationshipTo('SBQuestion', 'SELECTED_ANSWER_TO')

'''
@receiver(post_save, sender=SBPost)
def create_notification_post(sender, instance, **kwargs):
    from sb_notifications.tasks import prepare_post_notification_data
'''

