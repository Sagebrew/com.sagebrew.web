import pytz
import logging
from json import dumps
from datetime import datetime

from django.utils.text import slugify
from django.core.cache import cache

from boto.exception import BotoClientError, BotoServerError, AWSConnectionError
from boto.dynamodb2.exceptions import ProvisionedThroughputExceededException

from neo4j.v1 import CypherError
from neomodel import (StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty,
                      RelationshipFrom, db)


from sagebrew.sb_notifications.neo_models import NotificationCapable
from sagebrew.sb_docstore.utils import get_vote_count as doc_vote_count
from sagebrew.sb_votes.utils import determine_vote_type
from sagebrew.sb_tags.neo_models import TagRelevanceModel

from sagebrew.sb_base.decorators import apply_defense

logger = logging.getLogger('loggly_logs')


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
    This model is here because if we moved it to
    sagebrew.sb_council.neo_models it would cause circular dependencies.
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
    url = StringProperty()  # non api location
    href = StringProperty()  # api location
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
    owned_by = RelationshipTo('sagebrew.plebs.neo_models.Pleb', 'OWNED_BY',
                              model=PostedOnRel)
    votes = RelationshipFrom('sagebrew.plebs.neo_models.Pleb', 'PLEB_VOTES',
                             model=VoteRelationship)
    last_votes = RelationshipTo(
        'sagebrew.sb_votes.neo_models.Vote', 'LAST_VOTES')
    first_votes = RelationshipTo(
        'sagebrew.sb_votes.neo_models.Vote', 'FIRST_VOTES')
    # counsel_vote = RelationshipTo(
    # 'sagebrew.sb_council.neo_models.SBCounselVote', 'VOTE')
    # views = RelationshipTo('sagebrew.sb_views.neo_models.SBView', 'VIEWS')

    # methods
    def vote_content(self, vote_type, pleb):
        vote_active = "True"
        if vote_type == 2:
            vote_active = "False"
        query = 'MATCH (a:Pleb {username: "%s"}), ' \
                '(content:VotableContent {object_uuid: "%s"}) ' \
                'CREATE UNIQUE (a)-[rel:PLEB_VOTES]->(content) ' \
                'SET rel.active=%s RETURN rel' % (
                    pleb.username, self.object_uuid, vote_active)
        res, _ = db.cypher_query(query)
        return self

    def get_upvote_count(self):
        try:
            return int(doc_vote_count(self.object_uuid, 1))
        except(TypeError, IOError, BotoClientError, BotoServerError,
               AWSConnectionError, ProvisionedThroughputExceededException,
               Exception):  # pragma: no cover
            # Not covering this as we don't have a good way to shut down dynamo
            # run this and then recover. If someone can figure out a way to do
            # so please feel free. This has been tested in production and
            # staging under real life conditions - Devon Bleibtrey

            # We log this off because if we're receiving this error we may
            # want to increase the provisional count on DynamoDB
            logger.critical("DynamoDB Provision Throughput Reached or Down!")

            query = 'MATCH (b:VotableContent {object_uuid: "%s"})' \
                    '-[r:PLEB_VOTES]-(p:Pleb) ' \
                    'where r.vote_type=true and r.active=true return r' % (
                        self.object_uuid)
            try:
                res, _ = db.cypher_query(query)
                return len(res)
            except(CypherError, IOError) as e:
                logger.exception("Cypher Error: ")
                return e

    def get_downvote_count(self):
        try:
            return int(doc_vote_count(self.object_uuid, 0))
        except(TypeError, IOError, BotoClientError, BotoServerError,
               AWSConnectionError, ProvisionedThroughputExceededException,
               Exception):  # pragma: no cover
            # Not covering this as we don't have a good way to shut down dynamo
            # run this and then recover. If someone can figure out a way to do
            # so please feel free. This has been tested in production and
            # staging under real life conditions - Devon Bleibtrey

            # We log this off because if we're receiving this error we may
            # want to increase the provisional count on DynamoDB
            logger.critical("DynamoDB Provision Throughput Reached or Down!")

            query = 'MATCH (b:VotableContent {object_uuid: "%s"})' \
                    '-[r:PLEB_VOTES]-(p:Pleb) ' \
                    'where r.vote_type=false and r.active=true return r' % (
                        self.object_uuid)
            try:
                res, _ = db.cypher_query(query)
                return len(res)
            except (CypherError, IOError) as e:
                logger.exception("Cypher Error: ")
                return e

    def get_vote_count(self):
        return int(self.get_upvote_count() - self.get_downvote_count())

    def get_vote_type(self, username):
        try:
            return determine_vote_type(self.object_uuid, username)
        except(TypeError, IOError, BotoClientError, BotoServerError,
               AWSConnectionError, ProvisionedThroughputExceededException,
               Exception):  # pragma: no cover
            # Not covering this as we don't have a good way to shut down dynamo
            # run this and then recover. If someone can figure out a way to do
            # so please feel free. This has been tested in production and
            # staging under real life conditions - Devon Bleibtrey

            # We log this off because if we're receiving this error we may
            # want to increase the provisional count on DynamoDB
            logger.critical("DynamoDB Provision Throughput Reached!")
            query = 'MATCH (a:Pleb {username: "%s")-[rel:PLEB_VOTES]->' \
                    '(content:VotableContent {object_uuid: "%s"}) RETURN ' \
                    'CASE rel.active ' \
                    'WHEN False THEN NULL ' \
                    'ELSE rel.vote_type END' % (username, self.object_uuid)
            res, _ = db.cypher_query(query)
            return res[0][0] if res else None

    @apply_defense
    def get_rep_breakout(self):
        """
        This function will add up the amount of reputation that a user gets
        for a piece of content. It first checks to see if the content is closed
        and if 5 days have passed since the initial council vote was passed.
        If these two are true then the user is rewarded no reputation from
        the piece of content and loses 20 rep as per our content closure
        system.
        https://sagebrew.atlassian.net/wiki/display/RTS/Ability+to+Flag+Content
        :return:
        """
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

    def get_last_user_vote(self, username):
        from sagebrew.sb_votes.neo_models import Vote
        query = 'MATCH (a:VotableContent {object_uuid:"%s"})-[:LAST_VOTES]->' \
                '(v:Vote)-[:MADE_VOTE]->(p:Pleb {username:"%s"}) RETURN v' % \
                (self.object_uuid, username)
        res, _ = db.cypher_query(query)
        vote = res[0][0] if res else None
        if vote:
            return Vote.inflate(vote)
        return vote


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
    flagged_by = RelationshipTo('sagebrew.plebs.neo_models.Pleb', 'FLAGGED_BY')
    flags = RelationshipTo('sagebrew.sb_flags.neo_models.Flag', 'HAS_FLAG')
    comments = RelationshipTo(
        'sagebrew.sb_comments.neo_models.Comment', 'HAS_A',
        model=PostedOnRel)
    auto_tags = RelationshipTo('sagebrew.sb_tags.neo_models.Tag',
                               'AUTO_TAGGED_AS', model=TagRelevanceModel)
    rel_weight = RelationshipTo('sagebrew.plebs.neo_models.Pleb', 'HAS_WEIGHT',
                                model=RelationshipWeight)
    notifications = RelationshipTo(
        'sagebrew.sb_notifications.neo_models.Notification', 'NOTIFICATIONS')
    council_votes = RelationshipFrom(
        'sagebrew.plebs.neo_models.Pleb', 'COUNCIL_VOTE',
        model=CouncilVote)
    uploaded_objects = RelationshipTo(
        'sagebrew.sb_uploads.neo_models.UploadedObject',
        'UPLOADED_WITH')
    url_content = RelationshipTo('sagebrew.sb_uploads.neo_models.URLContent',
                                 'INCLUDED_URL_CONTENT')

    @classmethod
    def get_model_name(cls):
        return cls.__name__

    def update(self, instance):
        pass

    def create_notification(self, pleb):
        pass

    def reputation_adjust(self):
        pass

    def get_flagged_by(self):
        query = "MATCH (a:SBContent {object_uuid: '%s'})-[:FLAGGED_BY]->(" \
                "b:Pleb) Return b.username" % self.object_uuid
        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    def council_vote(self, vote_type, pleb):
        query = 'MATCH (a:Pleb {username: "%s"}), ' \
                '(content:SBContent {object_uuid: "%s"}) ' \
                'CREATE UNIQUE (a)-[rel:COUNCIL_VOTE]->(content) ' \
                'RETURN rel' % (pleb.username, self.object_uuid)
        res, _ = db.cypher_query(query)
        res = res[0][0] if res else None
        if res is not None:
            council_vote_rel = VoteRelationship.inflate(res)
            if vote_type == council_vote_rel.vote_type and \
                    council_vote_rel.active is True:
                council_vote_rel.active = False
            council_vote_rel.vote_type = vote_type
            council_vote_rel.save()
        return self

    def get_council_vote(self, username):
        query = 'MATCH (a:SBContent {object_uuid:"%s"})<-[r:COUNCIL_VOTE]-' \
                '(p:Pleb {username:"%s"}) WHERE r.active=true ' \
                'RETURN r.vote_type' % (self.object_uuid, username)
        res, _ = db.cypher_query(query)
        return res[0][0] if res else None

    def get_council_decision(self):
        # True denotes that the vote is for the content to be removed, while
        # false means that the content should not be removed
        query = 'MATCH (a:SBContent {object_uuid:"%s"})<-[rs:COUNCIL_VOTE]-' \
                '(p:Pleb) WHERE rs.active=true RETURN ' \
                'reduce(remove_vote = 0, r in collect(rs)| ' \
                'CASE WHEN r.vote_type=true THEN remove_vote+1 ' \
                'ELSE remove_vote END) as remove_vote, ' \
                'count(rs) as total_votes' \
                % self.object_uuid
        res, _ = db.cypher_query(query)
        try:
            percentage = float(
                res[0][0].remove_vote) / float(res[0][0].total_votes)
        except ZeroDivisionError:
            percentage = 0
        if percentage >= .66:
            return True
        return False

    @classmethod
    def get_mission(cls, object_uuid, request=None):
        from sagebrew.sb_missions.neo_models import Mission
        from sagebrew.sb_missions.serializers import MissionSerializer
        mission = cache.get("%s_mission" % object_uuid)
        if mission is None:
            query = 'MATCH (content:SBContent {object_uuid:"%s"})' \
                    '<-[:ASSOCIATED_WITH]-' \
                    '(mission:Mission) RETURN mission' % object_uuid
            res, _ = db.cypher_query(query)
            res = res[0][0] if res else None
            if res:
                mission = MissionSerializer(
                    Mission.inflate(res),
                    context={"request": request}).data
                cache.set("%s_mission" % object_uuid, mission)
        return mission

    def get_url(self, request):
        return None

    def get_uploaded_objects(self):
        from sagebrew.sb_uploads.neo_models import UploadedObject
        from sagebrew.sb_uploads.serializers import UploadSerializer
        query = 'MATCH (a:SBContent {object_uuid:"%s"})-' \
                '[:UPLOADED_WITH]->(u:UploadedObject) RETURN u' % \
                self.object_uuid
        res, _ = db.cypher_query(query)
        return [UploadSerializer(UploadedObject.inflate(row[0])).data
                for row in res]

    def get_url_content(self, single=False):
        from sagebrew.sb_uploads.neo_models import URLContent
        from sagebrew.sb_uploads.serializers import URLContentSerializer
        query = 'MATCH (a:SBContent {object_uuid:"%s"})-' \
                '[:INCLUDED_URL_CONTENT]->(u:URLContent) RETURN u' \
                % self.object_uuid
        res, _ = db.cypher_query(query)
        if single:
            try:
                return URLContentSerializer(
                    URLContent.inflate(res[0][0] if res else None)).data
            except AttributeError:
                return []
        return [URLContentSerializer(URLContent.inflate(row[0])).data
                for row in res]

    def get_participating_users(self):
        """
        This function will get all users involved in a comment thread on a
        specific object.

        :return:
        """
        query = 'MATCH (a:SBContent {object_uuid:"%s"})-[:HAS_A]->' \
                '(c:Comment) RETURN DISTINCT c.owner_username' \
                % self.object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]


class TaggableContent(SBContent):
    added_to_search_index = BooleanProperty(default=False)
    # relationships
    tags = RelationshipTo('sagebrew.sb_tags.neo_models.Tag', 'TAGGED_AS')

    # methods
    def add_auto_tags(self, tag_list):
        from sagebrew.sb_tags.neo_models import AutoTag
        auto_tag_list = []
        for tag in tag_list:
            name = slugify(tag['tags']['text'])
            query = 'MATCH (autotag:AutoTag {name: "%s"}) RETURN autotag' % (
                name
            )
            res, _ = db.cypher_query(query)
            if res[0][0] if res else None is None:
                AutoTag(name=name).save()
            res, _ = db.cypher_query(
                'MATCH (autotag:AutoTag {name: "%s"}),'
                ' (content:TaggableContent {object_uuid: "%s"}) '
                'CREATE UNIQUE (autotag)<-[rel:TAGGED_AS]-(content) '
                'SET rel.relevance=%f '
                'RETURN autotag' % (name, self.object_uuid,
                                    tag['tags']['relevance']))
            res = res[0][0] if res else None
            if res is not None:
                auto_tag_list.append(AutoTag.inflate(res if res else None))
        return auto_tag_list


class SBVersioned(TaggableContent):
    edit = lambda self: self.__class__.__name__
    original = BooleanProperty(default=True)
    draft = BooleanProperty(default=False)

    # relationships
    edits = RelationshipTo(SBContent.get_model_name(), 'EDIT')
    edit_to = RelationshipTo(SBContent.get_model_name(), 'EDIT_TO')


class SBPublicContent(SBVersioned):
    # Used to distinguish between private conversations and public
    pass


class TitledContent(SBPublicContent):
    title = StringProperty(index=True)


class SBPrivateContent(TaggableContent):
    # Used to distinguish between private conversations and public
    pass


def get_parent_titled_content(object_uuid):
    try:
        query = 'MATCH (a:TitledContent {object_uuid:"%s"}) return a' \
                % object_uuid
        res, _ = db.cypher_query(query)
        try:
            content = TitledContent.inflate(res[0][0] if res else None)
        except AttributeError as e:
            return e
        return content
    except (CypherError, IOError, IndexError) as e:
        return e


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
    except(CypherError, IOError, IndexError) as e:
        return e
