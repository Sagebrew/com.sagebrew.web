import math
import pytz
from logging import getLogger
from json import dumps
from datetime import datetime

from neomodel import (StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist, CardinalityViolation)
from neomodel import db

from sb_notifications.neo_models import NotificationCapable
from sb_docstore.utils import get_vote_count as doc_vote_count
from sb_votes.utils import determine_vote_type
from sb_tags.neo_models import TagRelevanceModel

from .decorators import apply_defense

logger = getLogger('loggly_logs')


def get_current_time():
    return datetime.now(pytz.utc)


def get_allowed_flags():
    return dumps(["explicit", "spam", "duplicate", "unsupported", "other"])


class RelationshipWeight(StructuredRel):
    weight = IntegerProperty(default=150)
    status = StringProperty(default='seen')
    seen = BooleanProperty(default=True)


class EditRelationshipModel(StructuredRel):
    time_edited = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class PostedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=get_current_time)
    rep_gained = IntegerProperty(default=0)
    rep_lost = IntegerProperty(default=0)


class VoteRelationship(StructuredRel):
    active = BooleanProperty(default=True)
    vote_type = BooleanProperty()  # True is up False is down
    rep_adjust = IntegerProperty()
    created = DateTimeProperty(default=get_current_time)


class CouncilVote(VoteRelationship):
    """
    This model is here because if we moved it to sb_council.neo_models it
    would cause circular dependencies.
    """
    reasoning = StringProperty()


class VotableContent(NotificationCapable):
    content = StringProperty()
    # Since both public and private content can be voted on this allows us to
    # filter out votable content that should have votes counted towards
    # reputation. Valid values are "private" and "public". We would be able
    # to rely on the public content being set to 0 but this doesn't hold true
    # for comments where they can be in public and private settings. We may
    # also utilize this strategy with public vs private conversations areas
    visibility = StringProperty(default="private")
    # Please use get_view_count rather than this. This currently has the view
    # count stored in it but that may change in the future as we transition
    # to a more discernible metrics approach.
    reputation_loss = IntegerProperty(default=0)

    up_vote_adjustment = IntegerProperty(default=0)
    down_vote_adjustment = IntegerProperty(default=0)
    down_vote_cost = IntegerProperty(default=0)
    is_closed = BooleanProperty(default=False)

    # optimizations
    owner_username = StringProperty()
    initial_vote_time = DateTimeProperty()
    # initial_vote_time is a property which lets us check if five days have
    # passed since the first council vote or if five days have passed since
    # the last time the task that checks for reputation recalculation has run.

    # relationships
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY',
                              model=PostedOnRel)
    votes = RelationshipFrom('plebs.neo_models.Pleb', 'PLEB_VOTES',
                             model=VoteRelationship)
    # counsel_vote = RelationshipTo('sb_council.neo_models.SBCounselVote',
    #                              'VOTE')
    # views = RelationshipTo('sb_views.neo_models.SBView', 'VIEWS')

    # methods
    def vote_content(self, vote_type, pleb):
        try:
            if self.votes.is_connected(pleb):
                rel = self.votes.relationship(pleb)
                if vote_type == 2:
                    return self.remove_vote(rel)
                rel.vote_type = vote_type
                rel.active = True
                rel.save()
            else:
                try:
                    rel = self.votes.connect(pleb)
                except CardinalityViolation:
                    rel = self.votes.relationship(pleb)
                rel.vote_type = vote_type
                rel.active = True
                if vote_type == 2:
                    rel.active = False
                rel.save()
            return self
        except (CypherException, IOError) as e:
            return e

    @apply_defense
    def remove_vote(self, rel):
        try:
            rel.active = False
            rel.save()
            return self
        except (CypherException, IOError) as e:
            return e

    @apply_defense
    def get_upvote_count(self):
        try:
            return int(doc_vote_count(self.object_uuid, 1))
        except(TypeError, IOError):
            logger.exception("DynamoDB Error: ")

        query = 'MATCH (b:VotableContent {object_uuid: "%s"})' \
                '-[r:PLEB_VOTES]-(p:Pleb) ' \
                'where r.vote_type=true and r.active=true return r' % (
                    self.object_uuid)
        try:
            res, col = self.cypher(query)
            return len(res)
        except(CypherException, IOError) as e:
            logger.exception("Cypher Error: ")
            return e

    @apply_defense
    def get_downvote_count(self):
        try:
            return int(doc_vote_count(self.object_uuid, 0))
        except(TypeError, IOError):
            logger.exception("DynamoDB Error: ")

        query = 'MATCH (b:VotableContent {object_uuid: "%s"})' \
                '-[r:PLEB_VOTES]-(p:Pleb) ' \
                'where r.vote_type=false and r.active=true return r' % (
                    self.object_uuid)
        try:
            res, col = self.cypher(query)
            return len(res)
        except (CypherException, IOError) as e:
            logger.exception("Cypher Error: ")
            return e

    @apply_defense
    def get_vote_count(self):
        return int(self.get_upvote_count() - self.get_downvote_count())

    @apply_defense
    def get_vote_type(self, username):
        from plebs.neo_models import Pleb
        try:
            return determine_vote_type(self.object_uuid, username)
        except(TypeError, IOError):
            logger.exception("DynamoDB Error: ")
        try:
            pleb = Pleb.get(username=username)
            if self.votes.is_connected(pleb):
                rel = self.votes.relationship(pleb)
            else:
                return None
        except(CypherException, IOError) as e:
            logger.exception("Cypher Error: ")
            return e
        if rel.active is False:
            return None
        return rel.vote_type

    @apply_defense
    def get_rep_breakout(self):
        '''
        This function will add up the amount of reputation that a user gets
        for a piece of content. It first checks to see if the content is closed
        and if 5 days have passed since the initial council vote was passed.
        If these two are true then the user is rewarded no reputation from
        the piece of content and loses 20 rep as per our content closure
        system.
        https://sagebrew.atlassian.net/wiki/display/RTS/Ability+to+Flag+Content
        :return:
        '''
        if self.is_closed and (datetime.now(pytz.utc) -
                               self.initial_vote_time).days >= 5:
            self.initial_vote_time = datetime.now(pytz.utc)
            self.save()
            return {
                'total_rep': -20,
                'pos_rep': 0,
                'neg_rep': -20
            }
        votes_up = self.get_upvote_count()
        votes_down = self.get_downvote_count()
        if isinstance(votes_up, Exception) is True:
            return votes_up
        if isinstance(votes_down, Exception) is True:
            return votes_down
        pos_rep = votes_up * int(self.up_vote_adjustment)
        neg_rep = votes_down * int(self.down_vote_adjustment)
        # Adding as it is expected that all down vote adjustments are negatives
        total_rep = pos_rep + neg_rep
        if total_rep < 0:
            total_rep = 0
        return {
            "total_rep": total_rep,
            "pos_rep": pos_rep,
            "neg_rep": neg_rep,
        }


class SBContent(VotableContent):
    allowed_flags = StringProperty(default=get_allowed_flags)
    last_edited_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    edited = BooleanProperty(default=False)
    to_be_deleted = BooleanProperty(default=False)
    is_explicit = BooleanProperty(default=False)
    is_removed = BooleanProperty(default=False)
    moderated_reason = StringProperty()

    polarity = FloatProperty()
    subjectivity = FloatProperty()
    # Please use get_vote_count rather than this. We have this included so that
    # we can update it at some future point in time. It hopefully will enable
    # us to order in the Neo4j query rather than using python if necessary like
    # we currently do for created and last edited on. However we need to
    # determine the potential for slippage from dynamo's count and how we want
    # to update it. So at the moment it will remain at 0.
    vote_count = IntegerProperty(default=0)

    # relationships
    flagged_by = RelationshipTo('plebs.neo_models.Pleb', 'FLAGGED_BY')
    flags = RelationshipTo('sb_flags.neo_models.Flag', 'HAS_FLAG')
    comments = RelationshipTo('sb_comments.neo_models.Comment', 'HAS_A',
                              model=PostedOnRel)
    auto_tags = RelationshipTo('sb_tags.neo_models.Tag',
                               'AUTO_TAGGED_AS', model=TagRelevanceModel)
    rel_weight = RelationshipTo('plebs.neo_models.Pleb', 'HAS_WEIGHT',
                                model=RelationshipWeight)
    notifications = RelationshipTo(
        'sb_notifications.neo_models.Notification', 'NOTIFICATIONS')
    council_votes = RelationshipTo('plebs.neo_models.Pleb', 'COUNCIL_VOTE',
                                   model=CouncilVote)
    uploaded_objects = RelationshipTo('sb_uploads.neo_models.UploadedObject',
                                      'UPLOADED_WITH')

    @classmethod
    def get_model_name(cls):
        return cls.__name__

    def update(self, instance):
        pass

    def create_notification(self, pleb):
        pass

    def reputation_adjust(self):
        pass

    @apply_defense
    def get_table(self):
        return self.table

    def get_flagged_by(self):
        query = "MATCH (a:SBContent {object_uuid: '%s'})-[:FLAGGED_BY]->(" \
                "b:Pleb) Return b.username" % (self.object_uuid)
        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    def council_vote(self, vote_type, pleb):
        try:
            if self.council_votes.is_connected(pleb):
                rel = self.council_votes.relationship(pleb)
                if vote_type == rel.vote_type and rel.active is True:
                    return self.remove_vote(rel)
                rel.vote_type = vote_type
                rel.active = True
            else:
                rel = self.council_votes.connect(pleb)
                if vote_type == rel.vote_type and rel.active is True:
                    rel.active = False
                rel.vote_type = vote_type
                rel.active = True
            rel.save()
            return self
        except (CypherException, IOError) as e:
            return e

    def get_council_vote(self, username):
        query = 'MATCH (a:SBContent {object_uuid:"%s"})-[r:COUNCIL_VOTE]->' \
                '(p:Pleb {username:"%s"}) WHERE r.active=true ' \
                'RETURN r.vote_type' % (self.object_uuid, username)
        res, _ = db.cypher_query(query)
        return res.one

    def get_council_decision(self):
        # True denotes that the vote is for the content to be removed, while
        # false means that the content should not be removed
        query = 'MATCH (a:SBContent {object_uuid:"%s"})-[rs:COUNCIL_VOTE]->' \
                '(p:Pleb) WHERE rs.active=true RETURN ' \
                'reduce(remove_vote = 0, r in collect(rs)| ' \
                'CASE WHEN r.vote_type=true THEN remove_vote+1 ' \
                'ELSE remove_vote END) as remove_vote, ' \
                'count(rs) as total_votes' \
                % self.object_uuid
        res, _ = db.cypher_query(query)
        try:
            percentage = float(res[0].remove_vote) / float(res[0].total_votes)
        except ZeroDivisionError:
            percentage = 0
        if percentage >= .66:
            return True
        return False

    def get_url(self, request):
        return None

    def get_uploaded_objects(self):
        from sb_uploads.neo_models import UploadedObject
        from sb_uploads.serializers import UploadSerializer
        query = 'MATCH (a:SBContent {object_uuid:"%s"})-' \
                '[:UPLOADED_WITH]->(u:UploadedObject) RETURN u' % \
                self.object_uuid
        res, col = db.cypher_query(query)
        try:
            return [UploadSerializer(UploadedObject.inflate(row[0])).data
                    for row in res]
        except IndexError:
            return []


class TaggableContent(SBContent):
    # relationships
    tags = RelationshipTo('sb_tags.neo_models.Tag', 'TAGGED_AS')
    added_to_search_index = BooleanProperty(default=False)

    # methods
    @apply_defense
    def add_tags(self, tags):
        """
        :param tags: String that contains a list of the tags being added with
                     a , representing the splitting point
        :return:
        """
        from sb_tags.neo_models import Tag
        tag_array = []
        if isinstance(tags, basestring) is True:
            tags = tags.split(',')
        if not tags:
            return False
        for tag in tags:
            try:
                tag_object = Tag.nodes.get(name=tag.lower())
                tag_array.append(tag_object)
            except (Tag.DoesNotExist, DoesNotExist):
                # TODO we should only be creating tags if the user has enough
                # rep
                continue
            except (CypherException, IOError) as e:
                return e
        for item in tag_array:
            try:
                self.tags.connect(item)
                item.tag_used += 1
                item.save()
            except (CypherException, IOError) as e:
                return e
        return tag_array

    def add_auto_tags(self, tag_list):
        from sb_tags.neo_models import AutoTag
        tag_array = []
        try:
            for tag in tag_list:
                try:
                    tag_object = AutoTag.nodes.get(
                        name=tag['tags']['text'].lower())
                except (AutoTag.DoesNotExist, DoesNotExist):
                    tag_object = AutoTag(
                        name=tag['tags']['text'].lower()).save()
                if self.auto_tags.is_connected(tag_object):
                    continue
                rel = self.auto_tags.connect(tag_object)
                rel.relevance = tag['tags']['relevance']
                rel.save()
                tag_array.append(tag_object)
            return tag_array
        except KeyError as e:
            return e


class SBVersioned(TaggableContent):
    edit = lambda self: self.__class__.__name__
    original = BooleanProperty(default=True)
    draft = BooleanProperty(default=False)

    # relationships
    edits = RelationshipTo(SBContent.get_model_name(), 'EDIT')
    edit_to = RelationshipTo(SBContent.get_model_name(), 'EDIT_TO')

    def edit_content(self, content, pleb):
        pass

    def get_name(self):
        return self.__class__.__name__

    def get_rep_breakout(self):
        """
        This reputation breakout is for determining how much rep falls under
        a given tag rather than an accumulation for analyzing an individuals
        reputation count. Not to be confused with the other get_rep_breakout.
        # TODO we may want to change the naming of this method
        :return:
        """
        if self.is_closed and (datetime.now(pytz.utc) -
                               self.initial_vote_time).days >= 5:
            self.initial_vote_time = datetime.now(pytz.utc)
            self.save()
            return {
                'total_rep': -20,
                'pos_rep': 0,
                'neg_rep': -20,
                'tag_list': [],
                'rep_per_tag': 0,
                'base_tag_list:': []
            }
        tag_list = []
        base_tags = []
        pos_rep = self.get_upvote_count() * int(self.up_vote_adjustment)
        neg_rep = self.get_downvote_count() * int(self.down_vote_adjustment)

        for tag in self.tags.all():
            if tag.base:
                base_tags.append(tag.name)
            tag_list.append(tag.name)
        try:
            rep_per_tag = math.ceil(float(pos_rep + neg_rep) / len(tag_list))
        except ZeroDivisionError:
            rep_per_tag = 0
        return {
            "total_rep": pos_rep + neg_rep,
            "pos_rep": pos_rep,
            "neg_rep": neg_rep,
            "tag_list": tag_list,
            "rep_per_tag": rep_per_tag,
            "base_tag_list": base_tags
        }


class SBPublicContent(SBVersioned):
    # Used to distinguish between private conversations and public
    pass


class TitledContent(SBPublicContent):
    title = StringProperty()


class SBPrivateContent(TaggableContent):
    # Used to distinguish between private conversations and public
    pass


def get_parent_content(object_uuid, relation, child_object):
    try:
        query = "MATCH (a:%s {object_uuid:'%s'})-[:%s]->" \
                "(b:SBContent) RETURN b" % (child_object, object_uuid, relation)
        res, col = db.cypher_query(query)
        try:
            content = SBContent.inflate(res[0][0])
        except ValueError:
            # This exception was added while initially implementing the fxn and
            # may not be possible in production. What happened was multiple
            # flags/votes got associated with a piece of content causing an
            # array to be returned instead of a single object which is handled
            # above. This should be handled now but we should verify that
            # the serializers ensure this singleness prior to removing this.
            content = SBContent.inflate(res[0][0][0])
        return content
    except(IndexError):
        return None


def get_parent_votable_content(object_uuid):
    try:
        query = 'MATCH (a:VotableContent {object_uuid:"%s"}) RETURN a' % (
            object_uuid)
        res, col = db.cypher_query(query)
        try:
            content = VotableContent.inflate(res[0][0])
        except ValueError:
            # This exception was added while initially implementing the fxn and
            # may not be possible in production. What happened was multiple
            # flags/votes got associated with a piece of content causing an
            # array to be returned instead of a single object which is handled
            # above. This should be handled now but we should verify that
            # the serializers ensure this singleness prior to removing this.
            content = VotableContent.inflate(res[0][0][0])
        return content
    except(CypherException, IOError, IndexError) as e:
        return e
