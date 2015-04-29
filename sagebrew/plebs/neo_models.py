import pytz
from datetime import datetime

from django.core.cache import cache
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty,
                      CypherException, DoesNotExist)
from neomodel import db

from api.neo_models import SBObject
from sb_search.neo_models import Searchable


def get_current_time():
    return datetime.now(pytz.utc)


class RelationshipWeight(StructuredRel):
    weight = IntegerProperty(default=150)
    status = StringProperty(default='seen')
    seen = BooleanProperty(default=True)


class SearchCount(StructuredRel):
    times_searched = IntegerProperty(default=1)
    last_searched = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class FriendRelationship(StructuredRel):
    since = DateTimeProperty(default=get_current_time)
    friend_type = StringProperty(default="friends")
    currently_friends = BooleanProperty(default=True)
    time_unfriended = DateTimeProperty(default=None)
    who_unfriended = StringProperty()
    # who_unfriended = RelationshipTo("Pleb", "")


class UserWeightRelationship(StructuredRel):
    interaction = StringProperty(default='seen')
    page_view_count = IntegerProperty(default=0)
    weight = IntegerProperty(default=settings.USER_RELATIONSHIP_BASE['seen'])


class TagRelationship(StructuredRel):
    total = IntegerProperty(default=0)
    rep_gained = IntegerProperty(default=0)
    rep_lost = IntegerProperty(default=0)


class PostObjectCreated(StructuredRel):
    shared_on = DateTimeProperty(default=get_current_time)
    rep_gained = IntegerProperty(default=0)
    rep_lost = IntegerProperty(default=0)


class ActionActiveRel(StructuredRel):
    gained_on = DateTimeProperty(default=get_current_time)
    active = BooleanProperty(default=True)
    lost_on = DateTimeProperty()


class RestrictionRel(StructuredRel):
    gained_on = DateTimeProperty(default=get_current_time)
    active = BooleanProperty()


class OfficialRelationship(StructuredRel):
    active = BooleanProperty(default=False)
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()


class OauthUser(SBObject):
    web_address = StringProperty(default=settings.WEB_ADDRESS + '/o/token/')
    access_token = StringProperty()
    expires_in = IntegerProperty()
    refresh_token = StringProperty()
    last_modified = DateTimeProperty(default=get_current_time)
    token_type = StringProperty(default="Bearer")


class BetaUser(StructuredNode):
    email = StringProperty(unique_index=True)
    invited = BooleanProperty(default=False)
    signup_date = DateTimeProperty(default=get_current_time)

    def invite(self):
        from sb_registration.utils import sb_send_email
        if self.invited is True:
            return True
        self.invited = True
        self.save()
        template_dict = {
            "signup_url": "%s%s%s" % (settings.WEB_ADDRESS, "/signup/?user=",
                                      self.email)
        }
        html_content = get_template(
            'email_templates/email_beta_invite.html').render(
            Context(template_dict))
        sb_send_email("support@sagebrew.com", self.email, "Sagebrew Beta",
                      html_content)
        return True


class Pleb(Searchable):
    """
    Signals and overwritting the save method don't seem to have any affect
    currently. We'll want to look into this and instead of having cache
    methods sprinkled around the code, overwrite get/save methods to first
    check the cache for the id of the object.
    Should also be updating/destroying the document in the search index upon
    save/update/destroy
    """
    search_modifiers = {
        'post': 10, 'comment_on': 5, 'upvote': 3, 'downvote': -3,
        'time': -1, 'proximity_to_you': 10, 'proximity_to_interest': 10,
        'share': 7, 'flag_as_inappropriate': -5, 'flag_as_spam': -100,
        'flag_as_other': -10, 'solution': 50, 'starred': 150, 'seen_search': 5,
        'seen_page': 20
    }
    gender = StringProperty()
    oauth_token = StringProperty()
    username = StringProperty(unique_index=True)
    first_name = StringProperty()
    last_name = StringProperty()
    middle_name = StringProperty()
    # Just an index as some individuals share email addresses still
    email = StringProperty(index=True)
    date_of_birth = DateTimeProperty()
    primary_phone = StringProperty()
    secondary_phone = StringProperty()
    profile_pic = StringProperty()
    profile_pic_uuid = StringProperty()
    wallpaper_pic = StringProperty()
    completed_profile_info = BooleanProperty(default=False)
    reputation = IntegerProperty(default=0)
    is_rep = BooleanProperty(default=False)
    is_admin = BooleanProperty(default=False)
    is_sage = BooleanProperty(default=False)
    search_index = StringProperty()
    # base_index_id is the plebs id in the base elasticsearch index
    base_index_id = StringProperty()
    email_verified = BooleanProperty(default=False)
    populated_personal_index = BooleanProperty(default=False)
    initial_verification_email_sent = BooleanProperty(default=False)
    stripe_customer_id = StringProperty()

    # Relationships
    privileges = RelationshipTo('sb_privileges.neo_models.Privilege', 'HAS',
                                model=ActionActiveRel)
    actions = RelationshipTo('sb_privileges.neo_models.SBAction', 'CAN',
                             model=ActionActiveRel)
    restrictions = RelationshipTo('sb_privileges.neo_models.Restriction',
                                  'RESTRICTED_BY', model=RestrictionRel)
    badges = RelationshipTo("sb_badges.neo_models.Badge", "BADGES")
    oauth = RelationshipTo("plebs.neo_models.OauthUser", "OAUTH_CLIENT")
    tags = RelationshipTo('sb_tags.neo_models.Tag', 'TAGS',
                          model=TagRelationship)
    voted_on = RelationshipTo('sb_base.neo_models.VotableContent', 'VOTES')
    address = RelationshipTo("Address", "LIVES_AT")
    interests = RelationshipTo("sb_tags.neo_models.Tag", "INTERESTED_IN")
    friends = RelationshipTo("Pleb", "FRIENDS_WITH", model=FriendRelationship)
    posts = RelationshipTo('sb_posts.neo_models.Post', 'OWNS_POST',
                           model=PostObjectCreated)
    questions = RelationshipTo('sb_questions.neo_models.Question',
                               'OWNS_QUESTION',
                               model=PostObjectCreated)
    solutions = RelationshipTo('sb_solutions.neo_models.Solution',
                               'OWNS_SOLUTION',
                               model=PostObjectCreated)
    comments = RelationshipTo('sb_comments.neo_models.Comment',
                              'OWNS_COMMENT',
                              model=PostObjectCreated)
    wall = RelationshipTo('sb_wall.neo_models.Wall', 'OWNS_WALL')
    notifications = RelationshipTo(
        'sb_notifications.neo_models.Notification', 'RECEIVED_A')
    friend_requests_sent = RelationshipTo(
        "plebs.neo_models.FriendRequest", 'SENT_A_REQUEST')
    friend_requests_received = RelationshipTo(
        "plebs.neo_models.FriendRequest", 'RECEIVED_A_REQUEST')
    user_weight = RelationshipTo('Pleb', 'WEIGHTED_USER',
                                 model=UserWeightRelationship)
    object_weight = RelationshipTo(
        'sb_base.neo_models.SBContent', 'OBJECT_WEIGHT',
        model=RelationshipWeight)
    searches = RelationshipTo('sb_search.neo_models.SearchQuery', 'SEARCHED',
                              model=SearchCount)
    clicked_results = RelationshipTo('sb_search.neo_models.SearchResult',
                                     'CLICKED_RESULT')
    official = RelationshipTo('sb_public_official.neo_models.PublicOfficial',
                              'IS_AUTHORIZED_AS', model=OfficialRelationship)
    senators = RelationshipTo('sb_public_official.neo_models.PublicOfficial',
                              'HAS_SENATOR')
    house_rep = RelationshipTo('sb_public_official.neo_models.PublicOfficial',
                               'HAS_HOUSE_REPRESENTATIVE')
    president = RelationshipTo('sb_public_official.neo_models.PublicOfficial',
                               'HAS_PRESIDENT')
    flags = RelationshipTo('sb_flags.neo_models.Flag', "FLAGS")
    beta_user = RelationshipTo('plebs.neo_models.BetaUser', "BETA_USER")

    def deactivate(self):
        return

    def is_beta_user(self):
        query = "MATCH (a:Pleb {username: '%s'})-[:BETA_USER]->(" \
                "b:BetaUser {email: '%s'}) " \
                "RETURN b" % (self.username, self.email)
        res, col = db.cypher_query(query)
        if len(res) == 0:
            return False
        return True

    def has_flagged_object(self, object_uuid):
        query = "MATCH (a:SBContent {object_uuid: '%s'})-[:FLAGGED_BY]->(" \
                "b:Pleb {username: '%s'}) Return b" % (
                    object_uuid, self.username)
        res, col = db.cypher_query(query)
        if len(res) == 0:
            return False
        return True

    def get_restrictions(self):
        return self.restrictions.all()

    def get_actions(self):
        query = 'MATCH (a:Pleb {username: "%s"})-' \
                '[:CAN {active: true}]->(n:`SBAction`) ' \
                'RETURN n.resource' % self.username
        res, col = db.cypher_query(query)
        if len(res) == 0:
            return []
        return [row[0] for row in res]

    def get_privileges(self):
        query = 'MATCH (a:Pleb {username: "%s"})-' \
                '[:HAS {active: true}]->(n:`Privilege`) ' \
                'RETURN n.name' % self.username
        res, col = db.cypher_query(query)
        if len(res) == 0:
            return []
        return [row[0] for row in res]

    def get_badges(self):
        return self.badges.all()

    def get_full_name(self):
        return str(self.first_name) + " " + str(self.last_name)

    def relate_comment(self, comment):
        try:
            rel_to_pleb = comment.owned_by.connect(self)
            rel_to_pleb.save()
            rel_from_pleb = self.comments.connect(comment)
            rel_from_pleb.save()
            return True
        except CypherException as e:
            return e

    def update_weight_relationship(self, sb_object, modifier_type):
        rel = self.object_weight.relationship(sb_object)
        if modifier_type in self.search_modifiers.keys():
            rel.weight += self.search_modifiers[modifier_type]
            rel.status = modifier_type
            rel.save()
            return rel.weight

    def get_votable_content(self):
        from sb_base.neo_models import VotableContent
        query = "MATCH (a:Pleb {username: '%s'})<-[:OWNED_BY]-(" \
                "b:VotableContent) RETURN b" % (self.username)
        res, col = db.cypher_query(query)

        return [VotableContent.inflate(row[0]) for row in res]

    def get_total_rep(self):
        rep_list = []
        base_tags = {}
        tags = {}
        original_rep = self.reputation
        total_rep = 0
        for item in self.get_votable_content():
            rep_res = item.get_rep_breakout()
            total_rep += rep_res['total_rep']
            if 'base_tag_list' in rep_res.keys():
                for base_tag in rep_res['base_tag_list']:
                    base_tags[base_tag] = rep_res['rep_per_tag']
                for tag in rep_res['tag_list']:
                    tags[tag] = rep_res['rep_per_tag']
            rep_list.append(rep_res)
        self.reputation = total_rep
        self.save()
        return {"rep_list": rep_list,
                "base_tags": base_tags,
                "tags": tags,
                "total_rep": total_rep,
                "previous_rep": original_rep}

    def get_object_rep_count(self):
        pass

    def update_tag_rep(self, base_tags, tags):
        from sb_tags.neo_models import Tag
        for item in tags:
            try:
                tag = Tag.nodes.get(name=item)
            except (Tag.DoesNotExist, DoesNotExist, CypherException, IOError):
                continue
            if self.tags.is_connected(tag):
                rel = self.tags.relationship(tag)
                rel.total = tags[item]
                rel.save()
            else:
                rel = self.tags.connect(tag)
                rel.total = tags[item]
                rel.save()
        for item in base_tags:
            try:
                tag = Tag.nodes.get(name=item)
            except (Tag.DoesNotExist, DoesNotExist, CypherException, IOError):
                continue
            if self.tags.is_connected(tag):
                rel = self.tags.relationship(tag)
                rel.total = base_tags[item]
                rel.save()
            else:
                rel = self.tags.connect(tag)
                rel.total = base_tags[item]
                rel.save()
        return True

    def get_available_flags(self):
        pass

    def vote_on_content(self, content):
        pass

    def get_question_count(self):
        return len(self.questions.all())

    def get_solution_count(self):
        return len(self.solutions.all())

    def get_post_count(self):
        return len(self.posts.all())

    def get_comment_count(self):
        return len(self.comments.all())

    def get_friends(self):
        return self.friends.all()

    def is_friends_with(self, username):
        query = "MATCH (a:Pleb {username:'%s'})-" \
                "[friend:FRIENDS_WITH]->(b:Pleb {username:'%s'}) " \
                "RETURN friend.currently_friends" % (self.username, username)
        res, col = db.cypher_query(query)
        if len(res) == 0:
            return False
        try:
            return res[0][0]
        except IndexError:
            return False

    def get_wall(self):
        '''
        Cypher Exception and IOError excluded on purpose, please do not add.
        The functions calling this expect the exceptions to be thrown and
        handle the exceptions on their own if they end up occuring.
        :return:
        '''
        from sb_wall.neo_models import Wall
        query = "MATCH (a:Pleb {username:'%s'})-" \
                "[:OWNS_WALL]->(b:Wall) RETURN b" % (self.username)
        res, col = db.cypher_query(query)
        try:
            return Wall.inflate(res[0][0])
        except IndexError:
            return None

    def get_friend_requests_sent(self, username):
        try:
            for friend_request in self.friend_requests_sent.all():
                try:
                    if friend_request.request_to.all()[0].username == username:
                        return friend_request.object_uuid
                except IndexError:
                    continue
        except(CypherException, IOError) as e:
            raise e
        return False

    def determine_reps(self):
        from sb_public_official.utils import determine_reps
        return determine_reps(self.username)

    def get_notifications(self):
        try:
            notification_list = []
            for notification in self.notifications.all():
                try:
                    # TODO see if we can do this with a serializer instead
                    from_user = notification.notification_from.all()[0]
                    notification_dict = {
                        "object_uuid": notification.object_uuid,
                        "notification_from": {
                            "profile_pic": from_user.profile_pic,
                            "first_name": from_user.first_name,
                            "last_name": from_user.last_name,
                            "username": from_user.username
                        },
                        "action_name": notification.action_name,
                        "url": notification.url,
                        "time_sent": notification.time_sent,
                        "time_seen": notification.time_seen,
                        "seen": notification.seen,
                        "about": notification.about,
                        "about_id": notification.about_id,
                    }
                    notification_list.append(notification_dict)
                except IndexError:
                    continue
        except(CypherException, IOError) as e:
            raise e
        return notification_list


class Address(SBObject):
    street = StringProperty()
    street_additional = StringProperty()
    city = StringProperty()
    state = StringProperty(index=True)
    postal_code = StringProperty(index=True)
    country = StringProperty()
    latitude = FloatProperty()
    longitude = FloatProperty()
    congressional_district = StringProperty()
    validated = BooleanProperty(default=True)

    # Relationships
    owned_by = RelationshipTo("Pleb", 'LIVES_IN')


class FriendRequest(SBObject):
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=get_current_time)
    time_seen = DateTimeProperty(default=None)
    response = StringProperty(default=None)

    # relationships
    request_from = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_FROM')
    request_to = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_TO')
