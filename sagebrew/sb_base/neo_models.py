import math
import pytz
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from elasticsearch import Elasticsearch

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist)

from sb_base.decorators import apply_defense


class EditRelationshipModel(StructuredRel):
    time_edited = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class PostedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    rep_gained = IntegerProperty(default=0)
    rep_lost = IntegerProperty(default=0)


class RelationshipWeight(StructuredRel):
    weight = IntegerProperty(default=150)
    status = StringProperty(default='seen')
    seen = BooleanProperty(default=True)


class VoteRelationship(StructuredRel):
    active = BooleanProperty(default=True)
    vote_type = BooleanProperty() # True is up False is down
    rep_adjust = IntegerProperty()
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class SBVoteableContent(StructuredNode):
    up_vote_adjustment = 0
    down_vote_adjustment = 0
    object_uuid = StringProperty(unique_index=True,
                                 default=lambda: str(uuid1()))
    content = StringProperty()
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

    # relationships
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY',
                              model=PostedOnRel)
    votes = RelationshipFrom('plebs.neo_models.Pleb', 'PLEB_VOTES',
                                model=VoteRelationship)
    # counsel_vote = RelationshipTo('sb_counsel.neo_models.SBCounselVote',
    #                              'VOTE')
    # views = RelationshipTo('sb_views.neo_models.SBView', 'VIEWS')

    #methods
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
        query = 'start s=node({self}) match s-[r:PLEB_VOTES]-(p:Pleb) ' \
                'where r.vote_type=true and r.active=true return r'
        try:
            res, col = self.cypher(query)
            return len(res)
        except CypherException as e:
            return e

    @apply_defense
    def get_downvote_count(self):
        query = 'start s=node({self}) match s-[r:PLEB_VOTES]-(p:Pleb) ' \
                'where r.vote_type=false and r.active=true return r'
        try:
            res, col = self.cypher(query)
            return len(res)
        except CypherException as e:
            return e

    @apply_defense
    def get_vote_count(self):
        try:
            return self.get_upvote_count() - self.get_downvote_count()
        except CypherException as e:
            return e

    @apply_defense
    def get_rep_breakout(self):
        pos_rep = self.get_upvote_count()*self.up_vote_adjustment
        neg_rep = self.get_downvote_count()*self.down_vote_adjustment
        return {
            "total_rep": pos_rep+neg_rep,
            "pos_rep": pos_rep,
            "neg_rep": neg_rep,
        }


class SBContent(SBVoteableContent):
    table = ''
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
    view_count_node = RelationshipTo('sb_stats.neo_models.SBViewCount',
                                     'VIEW_COUNT')
    flagged_by = RelationshipTo('plebs.neo_models.Pleb', 'FLAGGED_BY')
    flags = RelationshipTo('sb_flags.neo_models.SBFlag', 'HAS_FLAG')
    comments = RelationshipTo('sb_comments.neo_models.SBComment', 'HAS_A',
                              model=PostedOnRel)
    auto_tagged_as = RelationshipTo('sb_tag.neo_models.SBTag',
                                    'AUTO_TAGGED_AS')
    rel_weight = RelationshipTo('plebs.neo_models.Pleb', 'HAS_WEIGHT',
                                model=RelationshipWeight)
    notifications = RelationshipTo(
        'sb_notifications.neo_models.NotificationBase', 'NOTIFICATIONS')

    @classmethod
    def get_model_name(cls):
        return cls.__name__

    def create_notification(self, pleb):
        pass

    def create_relations(self, pleb, question=None, wall=None):
        try:
            self.owned_by.connect(pleb)
            return True
        except CypherException as e:
            return e

    @apply_defense
    def comment_on(self, comment):
        try:
            rel = self.comments.connect(comment)
            rel.save()

            return rel
        except CypherException as e:
            return e

    @apply_defense
    def delete_content(self, pleb):
        try:
            self.content=""
            self.to_be_deleted = True
            self.save()
            return self
        except CypherException as e:
            return e

    def reputation_adjust(self):
        pass

    @apply_defense
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

        except CypherException as e:
            return e

    def render_search(self):
        pass

    def render_single(self, pleb):
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

    def get_view_count(self):
        try:
            return self.view_count_node.all()[0].view_count
        except IndexError:
            return 0


class SBVersioned(SBContent):
    __abstract_node__ = True
    allowed_flags = ["explicit", "spam", "duplicate",
                     "unsupported", "other"]
    edit = lambda self: self.__class__.__name__
    original = BooleanProperty(default=True)
    draft = BooleanProperty(default=False)

    # relationships
    tagged_as = RelationshipTo('sb_tag.neo_models.SBTag', 'TAGGED_AS')
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
        for tag in self.tagged_as.all():
            if tag.base:
                base_tags.append(tag.tag_name)
            tag_list.append(tag.tag_name)
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


class SBNonVersioned(SBContent):
    allowed_flags = ["explicit", "spam", "other"]
    # relationships

    @apply_defense
    def edit_content(self, content, pleb):
        try:
            self.content = content
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return self
        except CypherException as e:
            return e


class SBTagContent(StructuredNode):
    # relationships
    tagged_as = RelationshipTo('sb_tag.neo_models.SBTag', 'TAGGED_AS')
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS')

    # methods
    @apply_defense
    def add_tags(self, tags):
        """
        :param tags: String that contains a list of the tags being added with
                     a , representing the splitting point
        :return:
        """
        from sb_tag.neo_models import SBTag
        tag_array = []
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        if not tags:
            return False
        for tag in tags:
            try:
                tag_object = SBTag.nodes.get(tag_name=tag)
                tag_array.append(tag_object)
            except (SBTag.DoesNotExist, DoesNotExist):
                es.index(index='tags', doc_type='tag',
                         body={'tag_name': tag})
                tag_object = SBTag(tag_name=tag).save()
                tag_array.append(tag_object)
            except CypherException as e:
                return e
        for item in tag_array:
            try:
                self.tagged_as.connect(item)
                item.tag_used += 1
                item.save()
            except CypherException as e:
                return e
        return tag_array

    def add_auto_tags(self, tag_list):
        from sb_tag.neo_models import SBAutoTag
        tag_array = []
        try:
            for tag in tag_list:
                try:
                    tag_object = SBAutoTag.nodes.get(tag_name=tag['tags']
                    ['text'])
                except (SBAutoTag.DoesNotExist, DoesNotExist):
                    tag_object = SBAutoTag(tag_name=tag['tags']['text']).save()
                if self.auto_tags.is_connected(tag_object):
                    continue
                rel = self.auto_tags.connect(tag_object)
                rel.relevance = tag['tags']['relevance']
                rel.save()
                tag_array.append(tag_object)
            return tag_array
        except KeyError as e:
            return e


