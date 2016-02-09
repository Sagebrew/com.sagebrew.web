import us
import pytz
from datetime import datetime

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.cache import cache
from django.templatetags.static import static

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      DoesNotExist, MultipleNodesReturned)
from neomodel import db

from api.utils import flatten_lists, spawn_task
from api.neo_models import SBObject
from sb_locations.neo_models import Location
from sb_search.neo_models import Searchable, Impression
from sb_base.neo_models import RelationshipWeight


def get_current_time():
    return datetime.now(pytz.utc)


def get_default_profile_pic():
    return static('images/sage_coffee_grey-01.png')


def get_default_wallpaper_pic():
    return static('images/wallpaper_western.jpg')


def get_friend_requests_sent(current_username, friend_username):
    query = "MATCH (a:Pleb {username: '%s'})-[:SENT_A_REQUEST]->" \
            "(f:FriendRequest)-[:REQUEST_TO]->(b:Pleb {username: '%s'}) " \
            "RETURN f.object_uuid" % (current_username, friend_username)
    res, col = db.cypher_query(query)
    if len(res) == 0:
        return False
    return res[0][0]


class SearchCount(StructuredRel):
    times_searched = IntegerProperty(default=1)
    last_searched = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class InterpersonalRelationship(StructuredRel):
    """
    Relationship base for handling relations between two or more people
    such as friends and followers/following.
    """
    since = DateTimeProperty(default=get_current_time)
    active = BooleanProperty(default=True)


class FriendRelationship(InterpersonalRelationship):
    friend_type = StringProperty(default="friends")
    time_unfriended = DateTimeProperty()
    who_unfriended = StringProperty()


class FollowRelationship(InterpersonalRelationship):
    get_notifications = BooleanProperty(default=False)
    # determine if the user wants to get notifications in their navbar


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
    profile_pic = StringProperty(default=get_default_profile_pic)
    wallpaper_pic = StringProperty(default=get_default_wallpaper_pic)
    completed_profile_info = BooleanProperty(default=False)
    reputation = IntegerProperty(default=0)
    is_rep = BooleanProperty(default=False)
    is_admin = BooleanProperty(default=False)
    is_sage = BooleanProperty(default=False)
    is_verified = BooleanProperty(default=True)
    search_index = StringProperty()
    reputation_update_seen = BooleanProperty(default=True)
    # Placeholders that enable us to gather a user's employer and
    # occupation if they are donating to a political campaign mission
    # We'll eventually be transitioning these to a node of their own.
    employer_name = StringProperty()
    occupation_name = StringProperty()
    # base_index_id is the plebs id in the base elasticsearch index
    base_index_id = StringProperty()
    email_verified = BooleanProperty(default=False)
    populated_personal_index = BooleanProperty(default=False)
    initial_verification_email_sent = BooleanProperty(default=False)

    stripe_customer_id = StringProperty()
    # The credit card associated with the customer
    stripe_default_card_id = StringProperty()
    # last_counted_vote_node is the node we want to query on to get
    # reputation change over time

    last_counted_vote_node = StringProperty(default=None)
    # vote_from_last_refresh is what gets stored every time a user
    # refreshes their page, allows us to easily swap it with
    # last_counted_vote_node when they check their reputation
    vote_from_last_refresh = StringProperty(default=None)
    mission_signup = StringProperty(default=None)

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
    viewed = RelationshipTo('sb_search.neo_models.Searchable', "VIEWED",
                            model=Impression)
    address = RelationshipTo("Address", "LIVES_AT")
    interests = RelationshipTo("sb_tags.neo_models.Tag", "INTERESTED_IN")
    friends = RelationshipTo("Pleb", "FRIENDS_WITH", model=FriendRelationship)
    # Optimization
    # Due to the large amounts of content it is more performant to explicitly
    # have relationships with each of the different pieces of content rather
    # than just OWNS
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
    # TODO our queries might not need HAS_SENATOR or HAS_HOUSE_REPRESENTATIVE
    # this distinction is covered by our endpoints of senators/house
    # representatives. We can change the relationship to REPRESENTED_BY
    # and utilize the Senate/House Representative/etc label to get the proper
    # official. This would require a Senator label though and not sure how we
    # want to handle this in a scalable way where we don't have to make new
    # relationships and classes for every new type of rep. Could potentially
    # define a few and then use a general class with an attribute that inherits
    # from them. Or we could start adding Labels that aren't associated with
    # classes based on the type of rep. This would allow us to use the same
    # types of queries and easily get all the types of representatives.
    senators = RelationshipTo('sb_public_official.neo_models.PublicOfficial',
                              'HAS_SENATOR')
    house_rep = RelationshipTo('sb_public_official.neo_models.PublicOfficial',
                               'HAS_HOUSE_REPRESENTATIVE')
    president = RelationshipTo('sb_public_official.neo_models.PublicOfficial',
                               'HAS_PRESIDENT')
    flags = RelationshipTo('sb_flags.neo_models.Flag', "FLAGS")
    beta_user = RelationshipTo('plebs.neo_models.BetaUser', "BETA_USER")
    uploads = RelationshipTo('sb_uploads.neo_models.UploadedObject', 'UPLOADS')
    url_content = RelationshipTo('sb_uploads.neo_models.URLContent',
                                 'URL_CONTENT')

    # Users can only have one campaign as the campaign is essentially their
    # action page and account information. They won't be able to create
    # multiple accounts or multiple action pages. We can then utilize the
    # campaign as another type of wall where they associate Projects or other
    # things to. If a user is waging a `PoliticalCampaign` their Action page
    # changes a little and they start being able to receive pledged votes and
    # there are more limitations on how donations occur.
    quest = RelationshipTo('sb_quests.neo_models.Quest', 'IS_WAGING')

    # Edits
    # Access if this Pleb can edit a Quest through:
    # Neomodel: editors Cypher: EDITOR_OF
    # RelationshipTo('sb_quests.neo_models.Quest')

    # Moderator
    # Access if this Pleb can view financial data of a Quest through:
    # Neomodel: moderators Cypher: MODERATOR_OF
    # RelationshipTo('sb_quests.neo_models.Quest')

    # Volunteer
    # Access what this Pleb has volunteered to do through:
    # Neomodel: volunteer Cypher: WANTS_TO
    # RelationshipFrom('sb_volunteers.neo_models.Volunteer')

    # Use stripe_account on quest instead
    stripe_account = StringProperty()
    # Can this just be a vote? Have it set like we do with votable content
    # with the assumption we can
    # utilize a different serializer that only enables up/off votes rather than
    # also allowing down votes to be cast. Then we can utilize the different
    # relationship to track any special items.
    donations = RelationshipTo('sb_donations.neo_models.Donation',
                               'DONATIONS_GIVEN')
    following = RelationshipTo('plebs.neo_models.Pleb', 'FOLLOWING',
                               model=FollowRelationship)
    party_affiliations = RelationshipTo('plebs.neo_models.PoliticalParty',
                                        'AFFILIATES_WITH')
    activity_interests = RelationshipTo('plebs.neo_models.ActivityInterest',
                                        'WILL_PARTICIPATE')

    @property
    def customer_token(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @classmethod
    def get(cls, username, cache_buster=False):
        profile = cache.get(username)
        if profile is None or cache_buster:
            res, _ = db.cypher_query(
                "MATCH (a:%s {username:'%s'}) RETURN a" % (
                    cls.__name__, username))
            if res.one:
                res.one.pull()
                profile = cls.inflate(res.one)
            else:
                raise DoesNotExist('Profile with username: %s '
                                   'does not exist' % username)
            cache.set(username, profile)
        return profile

    @classmethod
    def clear_unseen_friend_requests(cls, username):
        """
        This method sets all the existing friend requests a given Pleb has
        to seen. The method doesn't return anything because if the query fails
        it will throw a Cypher Exception which will be caught and handled by
        a view. Please wrap this function with the proper handler if you are
        calling it in a task.

        Limitations:
        This method requires that a username be passed rather than being
        executed on an initialized Pleb.

        Made this into a class method rather than a method that could be used
        on an initialized Pleb for optimization. Instead of querying a Pleb
        then having to execute this same query utilizing self.username it is
        more efficient to utilize a defined username that we can retrieve
        from something like request.user.username without having to get the
        Pleb. If there is want to transition this to a non-classmethod we
        could utilize the cache to get the initial Pleb and then call
        it based on that but that still runs the chance of executing two
        queries.

        :param username:
        :return:
        """
        value = get_current_time().astimezone(pytz.utc)
        epoch_date = datetime(1970, 1, 1, tzinfo=pytz.utc)
        time_seen = float((value - epoch_date).total_seconds())
        query = 'MATCH (a:Pleb {username: "%s"})-[:RECEIVED_A_REQUEST]->' \
                '(n:FriendRequest) WHERE n.seen=False' \
                ' SET n.seen = True, ' \
                'n.time_seen = %s' % (username, time_seen)
        db.cypher_query(query)

    @classmethod
    def get_mission_political_donations(cls, username, mission_id):
        donation_amount = cache.get('%s_%s_donation_amount' % (username,
                                                               mission_id))
        beg_year = datetime(datetime.now(pytz.utc).year, 1, 1).strftime("%s")
        end_year = datetime(datetime.now(pytz.utc).year + 1, 1, 1
                            ).strftime("%s")
        if donation_amount == 0 or donation_amount is None:
            query = 'MATCH (p:Pleb {username: "%s"})-[:DONATIONS_GIVEN]->' \
                    '(d:Donation)-[:DONATED_TO]->' \
                    '(c:Mission {object_uuid:"%s", ' \
                    'focus_on_type: "position"}) ' \
                    'WHERE d.created > %s AND d.created < %s ' \
                    'RETURN sum(d.amount)' \
                    % (username, mission_id, beg_year, end_year)
            res, col = db.cypher_query(query)
            donation_amount = res.one if res.one is not None else 0
            cache.set('%s_%s_donation_amount' %
                      (username, mission_id), donation_amount)
        return donation_amount

    def get_quest(self):
        query = 'MATCH (p:Pleb {username: "%s"})-[:IS_WAGING]->(c:Quest) ' \
                'RETURN c.owner_username' % self.username
        res, _ = db.cypher_query(query)
        return res.one

    def get_official_phone(self):
        query = 'MATCH (p:Pleb {username:"%s"})-[:IS_AUTHORIZED_AS]->' \
                '(o:PublicOfficial) RETURN o.gov_phone' % self.username
        res, _ = db.cypher_query(query)
        return res.one

    def deactivate(self):
        pass

    def get_address(self):
        query = 'MATCH (p:Pleb {username: "%s"})-[:LIVES_AT]->(a:Address) ' \
                'RETURN a' % self.username
        res, _ = db.cypher_query(query)
        try:
            return Address.inflate(res.one)
        except AttributeError:
            return None

    def is_beta_user(self):
        is_beta_user = cache.get("%s_is_beta" % self.username)
        if is_beta_user is None:
            query = "MATCH (a:Pleb {username: '%s'})-[:BETA_USER]->(" \
                "b:BetaUser {email: '%s'}) " \
                "RETURN b" % (self.username, self.email)
            res, col = db.cypher_query(query)
            if len(res) == 0:
                is_beta_user = False
            else:
                is_beta_user = True
            cache.set("%s_is_beta" % self.username, is_beta_user)
        # Have to cast to bool because memcache stores true and false as
        # integers
        return bool(is_beta_user)

    def get_actions(self, cache_buster=False):
        actions = cache.get("%s_actions" % self.username)
        if actions is None or cache_buster is True:
            query = 'MATCH (a:Pleb {username: "%s"})-' \
                    '[:CAN {active: true}]->(n:`SBAction`) ' \
                    'RETURN n.resource' % self.username
            res, col = db.cypher_query(query)
            actions = [row[0] for row in res]
            cache.set("%s_actions" % self.username, actions)
        return actions

    def get_privileges(self, cache_buster=False):
        privileges = cache.get("%s_privileges" % self.username)
        if privileges is None or cache_buster is True:
            query = 'MATCH (a:Pleb {username: "%s"})-' \
                    '[:HAS {active: true}]->(n:`Privilege`) ' \
                    'RETURN n.name' % self.username
            res, col = db.cypher_query(query)
            privileges = [row[0] for row in res]
            cache.set("%s_privileges" % self.username, privileges)
        return privileges

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

    def update_quest(self):
        query = 'MATCH (p:Pleb {username:"%s"})-[:IS_WAGING]->' \
                '(c:Quest) SET c.first_name="%s", c.last_name="%s"' % \
                (self.username, self.first_name, self.last_name)
        res, _ = db.cypher_query(query)
        return True

    def update_weight_relationship(self, sb_object, modifier_type):
        rel = self.object_weight.relationship(sb_object)
        if modifier_type in self.search_modifiers.keys():
            rel.weight += self.search_modifiers[modifier_type]
            rel.status = modifier_type
            rel.save()
            return rel.weight

    def get_votable_content(self):
        from sb_base.neo_models import VotableContent
        query = 'MATCH (a:Pleb {username: "%s"})<-[:OWNED_BY]-(' \
                'b:VotableContent) WHERE b.visibility = "public" RETURN b' \
                '' % self.username
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
            if isinstance(rep_res, Exception) is True:
                return rep_res
            total_rep += rep_res['total_rep']
            if 'base_tag_list' in rep_res.keys():
                for base_tag in rep_res['base_tag_list']:
                    base_tags[base_tag] = rep_res['rep_per_tag']
                for tag in rep_res['tag_list']:
                    tags[tag] = rep_res['rep_per_tag']
            rep_list.append(rep_res)
        if total_rep < 0:
            total_rep = 0
        self.reputation = total_rep
        self.save()
        cache.delete(self.username)
        return {"rep_list": rep_list,
                "base_tags": base_tags,
                "tags": tags,
                "total_rep": total_rep,
                "previous_rep": original_rep}

    def get_object_rep_count(self):
        pass

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
                "RETURN friend.active" % (self.username, username)
        res, col = db.cypher_query(query)
        if len(res) == 0:
            return False
        try:
            return res[0][0]
        except IndexError:
            return False

    def get_wall(self):
        """
        Cypher Exception and IOError excluded on purpose, please do not add.
        The functions calling this expect the exceptions to be thrown and
        handle the exceptions on their own if they end up occurring.
        :return:
        """
        from sb_wall.neo_models import Wall
        wall = cache.get("%s_wall" % self.username)
        if wall is None:
            query = "MATCH (a:Pleb {username:'%s'})-" \
                    "[:OWNS_WALL]->(b:Wall) RETURN b" % self.username
            res, col = db.cypher_query(query)
            try:
                wall = Wall.inflate(res[0][0])
                cache.set("%s_wall" % self.username, wall)
            except IndexError:
                # This may not be needed as the only way to get here is if
                # the wall was removed from the user or never created in the
                # first place. Since our tasks should never complete until a
                # wall has been created we shouldn't run into this. But to be
                # safe we've added it in. If we do manage to get here though
                # we may want to think about recovery methods or alerts we
                # should be sending out.
                return None
        return wall

    def get_friend_requests_sent(self, username):
        return get_friend_requests_sent(self.username, username)

    def determine_reps(self):
        from sb_public_official.utils import determine_reps
        return determine_reps(self)

    def get_donations(self):
        query = 'MATCH (p:Pleb {username: "%s"})-[:DONATIONS_GIVEN]->' \
                '(d:Donation)-[:CONTRIBUTED_TO]->(mission:Mission) ' \
                'RETURN d.object_uuid' % self.username
        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    def get_sagebrew_donations(self):
        query = 'MATCH (p:`Pleb` {username: "%s"})-[:DONATIONS_GIVEN]->' \
                '(d:`Donation`) WHERE NOT (d)-[:DONATED_TO]->(:Campaign) ' \
                'RETURN d.object_uuid' % self.username
        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    def is_authorized_as(self):
        from sb_public_official.neo_models import PublicOfficial
        official = cache.get("%s_official" % self.username)
        if official is None:
            query = 'MATCH (p:Pleb {username: "%s"})-[r:IS_AUTHORIZED_AS]->' \
                    '(o:PublicOfficial) WHERE r.active=true RETURN o' \
                    % self.username
            res, _ = db.cypher_query(query)
            try:
                official = PublicOfficial.inflate(res[0][0])
                cache.set("%s_official" % self.username, official)
            except IndexError:
                official = None
        return official

    def is_following(self, username):
        query = 'MATCH (p:Pleb {username:"%s"})<-[r:FOLLOWING]-' \
                '(p2:Pleb {username:"%s"}) RETURN r.active' % \
                (self.username, username)
        res, _ = db.cypher_query(query)
        return res.one

    def follow(self, username):
        """
        The username passed to this function is the user who will be following
        the user the method is called upon.
        :param username:
        """
        query = 'MATCH (p:Pleb {username:"%s"}), (p2:Pleb {username:"%s"}) ' \
                'WITH p, p2 CREATE UNIQUE (p)<-[r:FOLLOWING]-(p2) SET ' \
                'r.active=true RETURN r.active' % (self.username, username)
        res, _ = db.cypher_query(query)
        return res.one

    def unfollow(self, username):
        """
        The username passed to this function is the user who will stop
        following the user the method is called upon.
        :param username:
        """
        query = 'MATCH (p:Pleb {username:"%s"})<-[r:FOLLOWING]-(p2:Pleb ' \
                '{username:"%s"}) SET r.active=false RETURN r.active' \
                % (self.username, username)
        res, _ = db.cypher_query(query)
        return res.one

    @property
    def reputation_change(self):
        # See create_vote_node task in sb_votes tasks for where this is deleted
        res = cache.get("%s_reputation_change" % self.username)
        if res is None:
            query = 'MATCH (last_counted:Vote {object_uuid:"%s"})-' \
                    '[:CREATED_ON]->(s:Second) WITH s, last_counted MATCH ' \
                    '(s)-[:NEXT*]->(s2:Second)<-[:CREATED_ON]-(v:Vote)<-' \
                    '[:LAST_VOTES]-(content:VotableContent)-[:OWNED_BY]->' \
                    '(p:Pleb {username:"%s"}) WITH v ORDER BY v.created DESC ' \
                    'RETURN sum(v.reputation_change) ' \
                    'as rep_change, collect(v.object_uuid)[0] as last_created' \
                    % (self.last_counted_vote_node, self.username)
            res, _ = db.cypher_query(query)
            if not res:
                return 0
            # Have to cast to dict because pickle cannot handle the object
            # returned from cypher_query
            res = res[0].__dict__
            cache.set("%s_reputation_change" % self.username, res)
        reputation_change = res['rep_change']
        last_seen = res['last_created']
        if last_seen != self.vote_from_last_refresh:
            self.vote_from_last_refresh = res['last_created']
            self.save()
            cache.delete(self.username)
        if reputation_change >= 1000 or reputation_change <= -1000:
            return "%dk" % (int(reputation_change / 1000.0))
        return reputation_change

    def get_political_parties(self):
        query = "MATCH (a:Pleb {username:'%s'})-[:AFFILIATES_WITH]->" \
                "(b:PoliticalParty) RETURN b.name" % self.username
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    def get_activity_interests(self):
        query = "MATCH (a:Pleb {username:'%s'})-[:WILL_PARTICIPATE]->" \
                "(b:ActivityInterest) RETURN b.name" % self.username
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    """
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
    """


class Address(SBObject):
    street = StringProperty()
    street_additional = StringProperty()
    city = StringProperty()
    state = StringProperty(index=True)
    postal_code = StringProperty(index=True)
    country = StringProperty()
    latitude = FloatProperty()
    longitude = FloatProperty()
    county = StringProperty()
    congressional_district = IntegerProperty()
    validated = BooleanProperty(default=False)

    # Relationships
    owned_by = RelationshipTo("Pleb", 'LIVES_IN')
    encompassed_by = RelationshipTo('sb_locations.neo_models.Location',
                                    'ENCOMPASSED_BY')

    def get_all_encompassed_by(self):
        query = 'MATCH (a:Address {object_uuid:"%s"})-[:ENCOMPASSED_BY]->' \
                '(l:Location) WITH l OPTIONAL MATCH (l)-' \
                '[:ENCOMPASSED_BY*1..3]->(l2:Location) RETURN ' \
                'distinct l.object_uuid, collect(distinct(l2.object_uuid))'\
                % self.object_uuid
        res, _ = db.cypher_query(query)
        return flatten_lists(res)  # flatten

    def set_encompassing(self):
        from .tasks import connect_to_state_districts
        try:
            encompassed_by = Location.nodes.get(name=self.city)
            if Location.get_single_encompassed_by(
                    encompassed_by.object_uuid) != \
                    us.states.lookup(self.state).name:
                # if a location node exists with an incorrect encompassing
                # state
                raise DoesNotExist("This Location does not exist")
        except (Location.DoesNotExist, DoesNotExist):
            encompassed_by = Location(name=self.city, sector="local").save()
            city_encompassed = Location.nodes.get(
                name=us.states.lookup(self.state).name)
            if city_encompassed not in encompassed_by.encompassed_by:
                encompassed_by.encompassed_by.connect(city_encompassed)
            if encompassed_by not in city_encompassed.encompasses:
                city_encompassed.encompasses.connect(encompassed_by)
        except MultipleNodesReturned:
            query = 'MATCH (l1:Location {name:"%s"})-[:ENCOMPASSED_BY]->' \
                    '(l2:Location {name:"%s"}) RETURN l1' % \
                    (self.city, self.state)
            res, _ = db.cypher_query(query)
            if res.one is not None:
                encompassed_by = Location.inflate(res.one)
            else:
                encompassed_by = None
        if encompassed_by is not None:
            if encompassed_by not in self.encompassed_by:
                self.encompassed_by.connect(encompassed_by)
            if self not in encompassed_by.addresses:
                encompassed_by.addresses.connect(self)
        # get or create the state level districts and attach them to the
        # address
        spawn_task(task_func=connect_to_state_districts,
                   task_param={'object_uuid': self.object_uuid})
        return self


class FriendRequest(SBObject):
    seen = BooleanProperty(default=False)
    time_sent = DateTimeProperty(default=get_current_time)
    time_seen = DateTimeProperty()
    response = StringProperty(default=None)

    # relationships
    request_from = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_FROM')
    request_to = RelationshipTo('plebs.neo_models.Pleb', 'REQUEST_TO')

    @classmethod
    def unseen(cls, username):
        """
        Returns the amount of unseen friend requests for a given user
        :param username:
        :return:
        """
        query = 'MATCH (a:Pleb {username: "%s"})-[:RECEIVED_A_REQUEST]->' \
            '(n:FriendRequest) WHERE n.seen=False ' \
            'RETURN count(n)' % username
        res, col = db.cypher_query(query)
        return res[0][0]


class PoliticalParty(SBObject):
    name = StringProperty(unique_index=True)
    formal_name = StringProperty()

    # Relationship from Pleb to PoliticalParty:
    #   Python: party_affiliations
    #   Cypher: 'AFFILIATES_WITH'
    #   Example: (a:Pleb {username: "test_user"})-[:AFFILIATES_WITH]->
    #            (b:PoliticalParty)


class ActivityInterest(SBObject):
    name = StringProperty(unique_index=True)

    # Relationship from Pleb to ActivityInterest:
    #   Python: activity_interest
    #   Cypher: 'WILL_PARTICIPATE'
    #   Example: (a:Pleb {username: "test_user"})-[:WILL_PARTICIPATE]->
    #            (b:ActivityInterest)
