import pytz
from uuid import uuid1

from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty)


class EditRelationshipModel(StructuredRel):
    time_edited = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class PostedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class PostReceivedRel(StructuredRel):
    received = BooleanProperty()


class RelationshipWeight(StructuredRel):
    weight = IntegerProperty(default=150)
    status = StringProperty(default='seen')
    seen = BooleanProperty(default=True)


class SBBase(StructuredNode):
    sb_id = StringProperty(unique_index=True, default=lambda: str(uuid1()))
    content = StringProperty()
    date_created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    up_vote_number = IntegerProperty(default=0)
    down_vote_number = IntegerProperty(default=0)
    last_edited_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    edited = BooleanProperty(default=False)
    to_be_deleted = BooleanProperty(default=False)
    delete_time = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    is_explicit = BooleanProperty(default=False)
    polarity = FloatProperty()
    subjectivity = FloatProperty()
    flagged_as_spam_count = IntegerProperty(default=0)
    flagged_as_explicit_count = IntegerProperty(default=0)
    flagged_as_changed_count = IntegerProperty(default=0)
    flagged_as_unsupported_count = IntegerProperty(default=0)
    flagged_as_duplicate_count = IntegerProperty(default=0)
    flagged_as_other_count = IntegerProperty(default=0)
    view_count = IntegerProperty(default=0)


    # relationships
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS')
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY',
                              model=PostedOnRel)
    up_voted_by = RelationshipTo('plebs.neo_models.Pleb', 'UP_VOTED_BY')
    down_voted_by = RelationshipTo('plebs.neo_models.Pleb', 'DOWN_VOTED_BY')
    flagged_by = RelationshipTo('plebs.neo_models.Pleb', 'FLAGGED_BY')
    received_by = RelationshipTo('plebs.neo_models.Pleb', 'RECEIVED',
                                 model=PostReceivedRel)
    comments = RelationshipTo('sb_comments.neo_models.SBComment', 'HAS_A',
                              model=PostedOnRel)
    auto_tagged_as = RelationshipTo('sb_tag.neo_models.SBTag',
                                    'AUTO_TAGGED_AS')
    rel_weight = RelationshipTo('plebs.neo_models.Pleb', 'HAS_WEIGHT',
                                model=RelationshipWeight)
    notifications = RelationshipTo('sb_notifications.neo_models.NotificationBase',
                                   'NOTIFICATIONS')

class SBVersioned(SBBase):
    original = BooleanProperty(default=True)

    #relationships
    tagged_as = RelationshipTo('sb_tag.neo_models.SBTag', 'TAGGED_AS')

    def edit_content(self, content, pleb):
        pass

class SBNonVersioned(SBBase):
    #relationships
    auto_tagged_as = RelationshipTo('sb_tag.neo_models.SBTag',
                                    'AUTO_TAGGED_AS')

    def edit_content(self, content):
        self.content = content
        self.last_edited_on = datetime.now(pytz.utc)
        self.save()
        return self

class SBPost(SBNonVersioned):
    allowed_flags = ["explicit", "spam","other"]
    sb_name = "post"
    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.SBWall', 'POSTED_ON')
    #TODO Implement referenced_by_... relationships
    #TODO Implement ..._referenced relationships


'''
@receiver(post_save, sender=SBPost)
def create_notification_post(sender, instance, **kwargs):
    from sb_notifications.tasks import prepare_post_notification_data
'''

