import pytz

from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne)

class SBGarbageCan(StructuredNode):
    garbage_can = StringProperty(unique_index=True, default='garbage')

    #relationships
    posts = RelationshipTo('sb_posts.neo_models.SBPost', 'delete_post')
    comments = RelationshipTo('sb_comments.neo_models.SBComment', 'delete_comment')
    plebs = RelationshipTo('plebs.neo_models.Pleb', 'delete_user')
    questions = RelationshipTo('sb_posts.neo_models.SBPost', 'delete_question')
    answers = RelationshipTo('sb_posts.neo_models.SBPost', 'delete_answer')
    notifications = RelationshipTo('sb_notifications.neo_models.NotificationBase', 'delete_notification')

