import pytz
import logging
from json import dumps
from uuid import uuid1
from datetime import datetime
from django.conf import settings

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, db)

logger = logging.getLogger("loggly_logs")



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

class VoteRelationship(StructuredRel):
    active = BooleanProperty(default=True)
    vote_type = BooleanProperty() # True is up False is down None is undecided
    date_created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

class SBVoteableContent(StructuredNode):
    up_vote_adjustment = 0
    down_vote_adjustment = 0
    sb_id = StringProperty(unique_index=True, default=lambda: str(uuid1()))
    content = StringProperty()
    date_created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

    #relationships
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY',
                              model=PostedOnRel)
    votes = RelationshipFrom('plebs.neo_models.Pleb', 'PLEB_VOTES',
                                model=VoteRelationship)
    #counsel_vote = RelationshipTo('sb_counsel.neo_models.SBCounselVote',
    #                              'VOTE')
    #views = RelationshipTo('sb_views.neo_models.SBView', 'VIEWS')

    #methods
    def vote_content(self, vote_type, pleb):
        try:
            if self.votes.is_connected(pleb):
                rel = self.votes.relationship(pleb)
                if vote_type is rel.vote_type:
                    return self.remove_vote(rel)
                rel.vote_type = vote_type
                rel.active = True
                rel.save()
            else:
                rel = self.votes.connect(pleb)
                rel.vote_type = vote_type
                rel.active = True
                rel.save()
            return rel

        except Exception as e:
            logger.exception(dumps({"function": SBVoteableContent.vote_content.__name__,
                                    "exception": "Unhandled Exception"}))
            return e

    def remove_vote(self, rel):
        rel.active = False
        rel.save()
        return rel

    def get_upvote_count(self):
        query = 'start s=node({self}) match s-[r:PLEB_VOTES]-(p:Pleb) ' \
                'where r.vote_type=true and r.active=true return r'
        try:
            res, col = self.cypher(query)
            return len(res)
        except CypherException as e:
            return e

    def get_downvote_count(self):
        query = 'start s=node({self}) match s-[r:PLEB_VOTES]-(p:Pleb) ' \
                'where r.vote_type=false and r.active=true return r'
        try:
            res, col = self.cypher(query)
            return len(res)
        except CypherException as e:
            return e

    def get_vote_count(self):
        return self.get_upvote_count() - self.get_downvote_count()


class SBContent(SBVoteableContent):
    allowed_flags = []
    up_vote_number = IntegerProperty(default=0)
    down_vote_number = IntegerProperty(default=0)
    last_edited_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    edited = BooleanProperty(default=False)
    to_be_deleted = BooleanProperty(default=False)
    is_explicit = BooleanProperty(default=False)
    polarity = FloatProperty()
    subjectivity = FloatProperty()
    view_count = IntegerProperty(default=0)


    # relationships
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS')
    flagged_by = RelationshipTo('plebs.neo_models.Pleb', 'FLAGGED_BY')
    flags = RelationshipTo('sb_flags.neo_models.SBFlag', 'HAS_FLAG')
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

    @classmethod
    def get_model_name(cls):
        return cls.__name__

    def create_relations(self, pleb, question=None, wall=None):
        self.owned_by.connect(pleb)
        return self

    def comment_on(self, comment):
        try:
            rel = self.comments.connect(comment)
            rel.save()

            return rel
        except CypherException as e:
            return e
        except Exception as e:
            logger.exception(dumps({"function": SBContent.comment_on.__name__,
                                    "exception": "Unhandled Exception"}))
            return e

    def delete_content(self, pleb):
        try:
            self.content=""
            self.to_be_deleted = True
            self.save()
            return self
        except CypherException as e:
            return e
        except Exception as e:
            logger.exception(dumps({"function":
                                        SBContent.delete_content.__name__,
                                    "exception": "Unhandled Exception"}))
            return e

    def reputation_adjust(self):
        owner = self.owned_by.all()[0]
        pass

    def flag_content(self, flag_reason, current_pleb, description=""):
        from sb_flags.neo_models import SBFlag
        try:
            if flag_reason not in self.allowed_flags:
                return False

            if self.flagged_by.is_connected(current_pleb):
                return self

            flag = SBFlag(flag_reason=flag_reason, content=description).save()
            self.flags.connect(flag)
            self.flagged_by.connect(current_pleb)
            return self

        except Exception as e:
            logger.exception(dumps({"function": SBContent.flag_content.__name__,
                                    "exception": "Unhandled Exception"}))
            return e

    def render_search(self):
        pass

    def render_single(self, pleb):
        pass




class SBVersioned(SBContent):
    __abstract_node__ = True
    edit = lambda self: self.__class__.__name__
    original = BooleanProperty(default=True)
    draft = BooleanProperty(default=False)

    #relationships
    tagged_as = RelationshipTo('sb_tag.neo_models.SBTag', 'TAGGED_AS')
    edits = RelationshipTo(SBContent.get_model_name(), 'EDIT')
    edit_to = RelationshipTo(SBContent.get_model_name(), 'EDIT_TO')

    def edit_content(self, content, pleb):
        pass

    def get_name(self):
        return self.__class__.__name__




class SBNonVersioned(SBContent):
    #relationships
    auto_tagged_as = RelationshipTo('sb_tag.neo_models.SBTag',
                                    'AUTO_TAGGED_AS')

    def edit_content(self, content, pleb):
        try:
            self.content = content
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return self
        except CypherException as e:
            return e
        except Exception as e:
            return e
