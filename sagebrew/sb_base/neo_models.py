import math
import pytz
from logging import getLogger
from datetime import datetime
from django.conf import settings
from elasticsearch import Elasticsearch

from neomodel import (StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist)
from neomodel import db

from sb_notifications.neo_models import NotificationCapable
from sb_docstore.utils import get_vote_count as doc_vote_count
from sb_votes.utils import determine_vote_type
from sb_tag.neo_models import TagRelevanceModel
from plebs.neo_models import RelationshipWeight, Pleb

from .decorators import apply_defense

logger = getLogger('loggly_logs')


def get_current_time():
    return datetime.now(pytz.utc)


class EditRelationshipModel(StructuredRel):
    time_edited = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class PostedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=get_current_time)
    rep_gained = IntegerProperty(default=0)
    rep_lost = IntegerProperty(default=0)


class VoteRelationship(StructuredRel):
    active = BooleanProperty(default=True)
    vote_type = BooleanProperty() # True is up False is down
    rep_adjust = IntegerProperty()
    created = DateTimeProperty(default=get_current_time)


class VotableContent(NotificationCapable):
    up_vote_adjustment = 0
    down_vote_adjustment = 0
    content = StringProperty()
    view_count_node = RelationshipTo('sb_stats.neo_models.SBViewCount',
                                     'VIEW_COUNT')
    # relationships
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY',
                              model=PostedOnRel)
    votes = RelationshipFrom('plebs.neo_models.Pleb', 'PLEB_VOTES',
                             model=VoteRelationship)
    # counsel_vote = RelationshipTo('sb_counsel.neo_models.SBCounselVote',
    #                              'VOTE')
    # views = RelationshipTo('sb_views.neo_models.SBView', 'VIEWS')

    # methods
    @apply_defense
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
                rel = self.votes.connect(pleb)
                rel.vote_type = vote_type
                rel.active = True
                if vote_type == 2:
                    rel.active = False
                rel.save()
            return self
        except CypherException as e:
            return e

    @apply_defense
    def remove_vote(self, rel):
        try:
            rel.active = False
            rel.save()
            return self
        except CypherException as e:
            return e

    @apply_defense
    def get_upvote_count(self):
        try:
            return int(doc_vote_count(self.object_uuid, 1))
        except(TypeError, IOError):
            logger.exception("DynamoDB Error: ")

        query = 'start s=node({self}) match s-[r:PLEB_VOTES]-(p:Pleb) ' \
                'where r.vote_type=true and r.active=true return r'
        try:
            res, col = self.cypher(query)
            return len(res)
        except CypherException as e:
            logger.exception("Cypher Error: ")
            return e

    @apply_defense
    def get_downvote_count(self):
        try:
            return int(doc_vote_count(self.object_uuid, 0))
        except(TypeError, IOError):
            logger.exception("DynamoDB Error: ")

        query = 'start s=node({self}) match s-[r:PLEB_VOTES]-(p:Pleb) ' \
                'where r.vote_type=false and r.active=true return r'
        try:
            res, col = self.cypher(query)
            return len(res)
        except CypherException as e:
            logger.exception("Cypher Error: ")
            return e

    @apply_defense
    def get_vote_count(self):
        return int(self.get_upvote_count() - self.get_downvote_count())

    @apply_defense
    def get_vote_type(self, username):
        try:
            return determine_vote_type(self.object_uuid, username)
        except(TypeError, IOError):
            logger.exception("DynamoDB Error: ")
        try:
            pleb = Pleb.nodes.get(username=username)
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
        pos_rep = self.get_upvote_count()*self.up_vote_adjustment
        neg_rep = self.get_downvote_count()*self.down_vote_adjustment
        return {
            "total_rep": pos_rep+neg_rep,
            "pos_rep": pos_rep,
            "neg_rep": neg_rep,
        }

    def get_view_count(self):
        try:
            return self.view_count_node.all()[0].view_count
        except IndexError:
            return 0


class SBContent(VotableContent):
    allowed_flags = ["explicit", "spam", "duplicate",
                     "unsupported", "other"]
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
    # determine the potential for slippage from dyanmo's count and how we want
    # to update it. So at the moment it will remain at 0.
    vote_count = IntegerProperty(default=0)
    view_count = IntegerProperty(default=0)

    # relationships
    flagged_by = RelationshipTo('plebs.neo_models.Pleb', 'FLAGGED_BY')
    flags = RelationshipTo('sb_flags.neo_models.Flag', 'HAS_FLAG')
    comments = RelationshipTo('sb_comments.neo_models.Comment', 'HAS_A',
                              model=PostedOnRel)
    auto_tags = RelationshipTo('sb_tag.neo_models.Tag',
                               'AUTO_TAGGED_AS', model=TagRelevanceModel)
    rel_weight = RelationshipTo('plebs.neo_models.Pleb', 'HAS_WEIGHT',
                                model=RelationshipWeight)
    notifications = RelationshipTo(
        'sb_notifications.neo_models.NotificationBase', 'NOTIFICATIONS')

    @classmethod
    def get_model_name(cls):
        return cls.__name__

    def create_notification(self, pleb):
        pass

    def reputation_adjust(self):
        pass

    @apply_defense
    def get_table(self):
        return self.table

    @apply_defense
    def create_view_count(self):
        from sb_stats.neo_models import SBViewCount
        try:
            count_node = SBViewCount().save()
        except (CypherException, IOError) as e:
            return e
        try:
            self.view_count_node.connect(count_node)
        except (CypherException, IOError) as e:
            return e
        return True

    def increment_view_count(self):
        try:
            return self.view_count_node.all()[0].increment()
        except IndexError:
            return 0

    def get_flagged_by(self):
        query = "MATCH (a:SBContent {object_uuid: '%s'})-[:FLAGGED_BY]->(" \
                "b:Pleb) Return b" % (self.object_uuid)
        res, col = db.cypher_query(query)
        if len(res) == 0:
            return []
        return res

    def get_labels(self):
        query = 'START n=node(%d) RETURN DISTINCT labels(n)' % (self._id)
        res, col = db.cypher_query(query)
        return res[0][0]

    def get_child_label(self):
        """
        With the current setup the actual piece of content is the last
        label.

        This goes on the assumption that Neo4J returns labels in order of
        assignment. Since neomodel assigns these in order of inheritance
        the top most parent being first and the bottom child being last
        we assume that our actual real commentable object is last.

        This can be accomplished by ensuring that the content is the
        bottom most child in the hierarchy. Currently this is only used for
        determining what content a comment is actually associated with for
        url linking. The commented out logic below can be substituted if with
        a few additional items if this begins to not work

            def get_child_labels(self):
                parents = inspect.getmro(self.__class__)
                # Creates a generator that enables us to access all the
                # names of the parent classes
                parent_array = (o.__name__ for o in parents)
                child_array = list(set(self.get_labels()) - set(parent_array))
                return child_array

            def get_child_label(self):
                labels = self.get_labels()
                # If you want to comment on something the class name must be
                # listed here
                content = ['Post', 'Question', 'Solution']
                try:
                    set(labels).intersection(content).pop()
                except KeyError:
                    return ""

        :return:
        """
        return list(set(self.get_labels()) - set(settings.REMOVE_CLASSES))[0]


class TaggableContent(SBContent):
    # relationships
    tags = RelationshipTo('sb_tag.neo_models.Tag', 'TAGGED_AS')
    added_to_search_index = BooleanProperty(default=False)

    # methods
    @apply_defense
    def add_tags(self, tags):
        """
        :param tags: String that contains a list of the tags being added with
                     a , representing the splitting point
        :return:
        """
        from sb_tag.neo_models import Tag
        tag_array = []
        if isinstance(tags, basestring) is True:
            tags = tags.split(',')
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        if not tags:
            return False
        for tag in tags:
            try:
                tag_object = Tag.nodes.get(name=tag.lower())
                tag_array.append(tag_object)
            except (Tag.DoesNotExist, DoesNotExist):
                # TODO we should only be creating tags if the user has enough
                # rep
                pass
            except CypherException as e:
                return e
        for item in tag_array:
            try:
                self.tags.connect(item)
                item.tag_used += 1
                item.save()
            except CypherException as e:
                return e
        return tag_array

    def add_auto_tags(self, tag_list):
        from sb_tag.neo_models import AutoTag
        tag_array = []
        try:
            for tag in tag_list:
                try:
                    tag_object = AutoTag.nodes.get(name=tag['tags']
                    ['text'].lower())
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
        tag_list = []
        base_tags = []
        pos_rep = self.get_upvote_count()*self.up_vote_adjustment
        neg_rep = self.get_downvote_count()*self.down_vote_adjustment
        for tag in self.tags.all():
            if tag.base:
                base_tags.append(tag.name)
            tag_list.append(tag.name)
        try:
            rep_per_tag = math.ceil(float(pos_rep+neg_rep)/len(tag_list))
        except ZeroDivisionError:
            rep_per_tag = 0
        return {
            "total_rep": pos_rep+neg_rep,
            "pos_rep": pos_rep,
            "neg_rep": neg_rep,
            "tag_list": tag_list,
            "rep_per_tag": rep_per_tag,
            "base_tag_list": base_tags
        }


class SBPublicContent(SBVersioned):
    # Used to distinguish between private conversations and public
    pass


class SBPrivateContent(TaggableContent):
    # Used to distinguish between private conversations and public
    pass


def get_parent_content(object_uuid, relation, child_object):
    try:
        query = "MATCH (a:%s {object_uuid:'%s'})-[:%s]->" \
                "(b:SBContent) RETURN b" % (object_uuid, child_object, relation)
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


def get_parent_votable_content(object_uuid, relation, child_object):
    try:
        query = "MATCH (a:%s {object_uuid:'%s'})-[:%s]->" \
                "(b:VotableContent) RETURN b" % (object_uuid, child_object,
                                                 relation)
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
    except(IndexError):
        return None