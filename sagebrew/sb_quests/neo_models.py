from django.contrib.humanize.templatetags.humanize import ordinal
from django.core.cache import cache
from django.conf import settings
from django.templatetags.static import static

from rest_framework.reverse import reverse

from neomodel import (db, StringProperty, RelationshipTo, BooleanProperty,
                      FloatProperty, DoesNotExist, RelationshipFrom,
                      DateTimeProperty, ArrayProperty)

from sagebrew.sb_search.neo_models import Searchable, SBObject


def get_default_wallpaper_pic():
    return static(settings.DEFAULT_WALLPAPER)


class Quest(Searchable):
    """
    A Quest is about the individual or group and tracking thier progress
    over the years. See Missions for their specific endeavours.
    """
    # Stripe managed account id
    stripe_id = StringProperty(index=True, default="Not Set")
    # Stripe customer id (used to charge subscriptions against)
    stripe_customer_id = StringProperty()
    # Subscription ID for retrieving and managing subscription
    stripe_subscription_id = StringProperty()
    # The credit card associated with the quest
    stripe_default_card_id = StringProperty()
    stripe_identification_sent = BooleanProperty(default=False)
    # Did the user accept the Stripe Terms of Service?
    tos_acceptance = BooleanProperty(default=False)
    # Stripe Account Type valid options:
    #     business
    #     individual
    stripe_account_type = StringProperty(default="business")
    account_owner = StringProperty()
    # Has stripe verified the account we are managing for the Quest yet?
    # TODO this should get set by a callback listener that watches for
    # Stripe to send back a verified notification. Then if stripe say it's
    # not verified we can alert the user to the issue
    # Valid options are:
    #     unverified
    #     pending
    #     verified
    account_verified = StringProperty(default="unverified")
    # fields_needed contains a string which states what is needed for an
    # account to get verified
    account_verification_fields_needed = ArrayProperty()
    # A user readable string which states the reason verification has failed.
    account_verification_details = StringProperty()
    account_first_updated = DateTimeProperty(default=None)
    account_verified_date = DateTimeProperty()
    verification_document_needed = BooleanProperty(default=False)
    verification_due_date = DateTimeProperty(default=None)
    verification_disabled_reason = StringProperty()
    # Valid options are:
    #     free
    #     paid
    #     promotion
    #     custom
    account_type = StringProperty()
    # A Quest is always active after the stripe account has been activated.
    # A Quest must have a Mission to take donations towards.
    # TODO can we remove active?
    active = BooleanProperty(default=False)
    facebook = StringProperty()
    linkedin = StringProperty()
    youtube = StringProperty()
    twitter = StringProperty()
    website = StringProperty()
    # About is a short string that allows the Quest to describe itself in 128
    # characters
    about = StringProperty()
    # These are the wallpaper and profile specific to the campaign/action page
    # That way they have separation between the campaign and their personal
    # image.
    wallpaper_pic = StringProperty(default=get_default_wallpaper_pic)
    profile_pic = StringProperty()
    # Application fee's total up to 5% + 30 cents for both Quest accounts
    # .029 and the 30 comes from
    # stripe. 0.021 and 0.021 respectively come from us.
    application_fee = FloatProperty(default=0.021)
    last_four_soc = StringProperty()

    # Optimizations
    # Seat name and formal name have taken the place of position and are for
    # storing the title of the seat a Quest currently holds.
    seat_name = StringProperty()
    seat_formal_name = StringProperty()

    # Since a Quest can be associated with a group let's give them the option
    # to set a title.
    title = StringProperty()
    # First and Last name are added to reduce potential additional queries
    # when rendering potential representative html to a users profile page
    first_name = StringProperty()
    last_name = StringProperty()
    owner_username = StringProperty()

    # TEMPORARY
    ssn_temp = StringProperty()
    bank_account_temp = StringProperty()
    routing_number_temp = StringProperty()

    # Relationships
    # Donations
    # Access Donations that are related to this Quest through:
    # Neomodel: quest Cypher: CONTRIBUTED_TO
    # RelationshipTo('sagebrew.sb_donations.neo_models.Donation')

    updates = RelationshipTo('sagebrew.sb_updates.neo_models.Update', 'CREATED_AN')

    # Pleb
    # Access the Pleb that owns this Quest through:
    # Neomodel: quest Cypher: IS_WAGING
    # RelationshipTo('sagebrew.sb_plebs.neo_models.Pleb')

    # Will be an endpoint with the usernames of all the users that can edit
    # the page. That way we can easily check who has the right to modify
    # the page. These names should not be public
    editors = RelationshipFrom('sagebrew.plebs.neo_models.Pleb', 'EDITOR_OF')
    moderators = RelationshipFrom(
        'sagebrew.plebs.neo_models.Pleb', 'MODERATOR_OF')

    address = RelationshipTo(
        "sagebrew.sb_address.neo_models.Address", 'LOCATED_AT')

    # Embarks on is a mission this Quest manages and is trying to accomplish.
    # Donations to these missions come back to the Quest's account
    missions = RelationshipTo(
        'sagebrew.sb_missions.neo_models.Mission', "EMBARKS_ON")
    holds = RelationshipTo(
        'sagebrew.sb_quests.neo_models.Seat', "HOLDS")
    news_articles = RelationshipTo(
        'sagebrew.sb_news.neo_models.NewsArticle', "NEWS")
    # Followers are users which have decided to follow a Quest, this means that
    # they will get a notification whenever the quest makes an update.
    followers = RelationshipTo('sagebrew.plebs.neo_models.Pleb', "FOLLOWERS")

    # Owner of the Quest
    owner = RelationshipFrom('sagebrew.plebs.neo_models.Pleb', 'IS_WAGING')

    @property
    def ein(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def ssn(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def stripe_token(self):  # pragma: no cover
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def customer_token(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def routing_number(self):  # pragma: no cover
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def account_number(self):  # pragma: no cover
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def promotion_key(self):  # pragma: no cover
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @classmethod
    def get(cls, owner_username, cache_buster=False):
        quest = None
        if cache_buster is False:
            quest = cache.get("%s_quest" % owner_username)
        if quest is None or cache_buster:
            query = 'MATCH (c:Quest {owner_username: "%s"}) RETURN c' % \
                    owner_username
            res, _ = db.cypher_query(query)
            if res.one:
                res.one.pull()
                quest = cls.inflate(res.one)
                cache.set("%s_quest" % owner_username, quest)
            else:
                raise DoesNotExist("Quest does not exist")
        return quest

    @classmethod
    def get_editors(cls, owner_username):
        editors = cache.get("%s_editors" % owner_username)
        if editors is None:
            query = 'MATCH (c:Quest {owner_username: "%s"})<-' \
                    '[:EDITOR_OF]-(p:Pleb) RETURN p.username' % (
                        owner_username)
            res, col = db.cypher_query(query)
            editors = [row[0] for row in res]
            cache.set("%s_editors" % owner_username, editors)
        return editors

    @classmethod
    def get_moderators(cls, owner_username):
        moderators = cache.get("%s_moderators" % owner_username)
        if moderators is None:
            query = 'MATCH (c:Quest {owner_username: "%s"})<-' \
                    '[:MODERATOR_OF]-(p:Pleb) RETURN p.username' \
                    % owner_username
            res, col = db.cypher_query(query)
            moderators = [row[0] for row in res]
            cache.set("%s_moderators" % owner_username, moderators)
        return moderators

    @classmethod
    def get_quest_helpers(cls, object_uuid):
        return cls.get_moderators(object_uuid) + cls.get_editors(object_uuid)

    @classmethod
    def get_url(cls, object_uuid, request):
        query = 'MATCH (c:Quest {object_uuid:"%s"})<-' \
                '[:IS_WAGING]-(p:Pleb) return p.username' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return reverse('quest', kwargs={"username": res.one},
                           request=request)
        except IndexError:
            return None

    @classmethod
    def get_updates(cls, object_uuid):
        updates = cache.get("%s_updates" % object_uuid)
        if updates is None:
            query = 'MATCH (c:Quest {object_uuid:"%s"})-[:CREATED_AN]->' \
                    '(u:Update) WHERE u.to_be_deleted=false ' \
                    'RETURN u.object_uuid' % object_uuid
            res, col = db.cypher_query(query)
            updates = [row[0] for row in res]
            cache.set("%s_updates" % object_uuid, updates)
        return updates

    @classmethod
    def get_donations(cls, owner_username):
        from sagebrew.sb_donations.neo_models import Donation
        query = 'MATCH (c:Quest {owner_username:"%s"})-[:EMBARKS_ON]->' \
                '(mission:Mission)<-' \
                '[:CONTRIBUTED_TO]-(d:Donation) RETURN d' % owner_username
        res, _ = db.cypher_query(query)
        return [Donation.inflate(donation[0]) for donation in res]

    def is_following(self, username):
        following = cache.get("%s_is_following_quest_%s" %
                              (username, self.object_uuid))
        if following is None:
            query = 'MATCH (q:Quest {object_uuid:"%s"})-[r:FOLLOWERS]->' \
                    '(p:Pleb {username:"%s"}) RETURN r.active' % \
                    (self.object_uuid, username)
            res, _ = db.cypher_query(query)
            following = res.one
            if following is None:
                following = False
            cache.set("%s_is_following_quest_%s" % (username, self.object_uuid),
                      following)
        return following

    def follow(self, username):
        """
        The username passed to this function is the user who will be following
        the user the method is called upon.
        :param username:
        """
        query = 'MATCH (q:Quest {object_uuid:"%s"}), ' \
                '(p:Pleb {username:"%s"}) ' \
                'WITH q, p CREATE UNIQUE (q)-[r:FOLLOWERS]->(p) SET ' \
                'r.active=true RETURN r.active' % (self.object_uuid, username)
        res, _ = db.cypher_query(query)
        cache.delete("%s_is_following_quest_%s" % (username, self.object_uuid))
        return res.one

    def unfollow(self, username):
        """
        The username passed to this function is the user who will stop
        following the user the method is called upon.
        :param username:
        """
        query = 'MATCH (q:Quest {object_uuid:"%s"})-[r:FOLLOWERS]->(p:Pleb ' \
                '{username:"%s"}) SET r.active=false RETURN r.active' \
                % (self.object_uuid, username)
        res, _ = db.cypher_query(query)
        cache.delete("%s_is_following_quest_%s" % (username, self.object_uuid))
        return res.one

    def get_followers(self):
        query = 'MATCH (q:Quest {object_uuid:"%s"})-[r:FOLLOWERS]->' \
                '(p:Pleb) WHERE r.active=true RETURN p.username' % \
                self.object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    def get_total_donation_amount(self):
        query = 'MATCH (c:Quest {object_uuid:"%s"})-[:EMBARKS_ON]' \
                '->(mission:Mission)<-' \
                '[:CONTRIBUTED_TO]-(d:Donation) ' \
                'RETURN sum(d.amount) - (sum(d.amount) * ' \
                '(%f + %f) + count(d) * 30)' % (
                    self.object_uuid, self.application_fee,
                    settings.STRIPE_TRANSACTION_PERCENT)
        res, _ = db.cypher_query(query)
        if res.one:
            return '{:,.2f}'.format(float(res.one) / 100)
        else:
            return "0.00"


class Position(SBObject):
    name = StringProperty()
    full_name = StringProperty()
    verified = BooleanProperty(default=True)
    user_created = BooleanProperty(default=False)
    # Valid Options:
    #     executive
    #     legislative
    #     judicial
    #     enforcement
    office_type = StringProperty(default="executive")
    # Valid Levels:
    #     state_upper - State Senator Districts
    #     state_lower - State House Representative Districts
    #     federal - U.S. Federal Districts (House of Reps)
    #     local - Everything else :)
    level = StringProperty(default="federal")

    location = RelationshipFrom('sagebrew.sb_locations.neo_models.Location',
                                'POSITIONS_AVAILABLE')
    currently_held_by = RelationshipTo('sagebrew.sb_public_official.neo_models.'
                                       'PublicOfficial', "CURRENTLY_HELD_BY")
    restrictions = RelationshipTo('sagebrew.sb_privileges.neo_models.Restriction',
                                  'RESTRICTED_BY')
    seats = RelationshipTo('sagebrew.sb_quests.neo_models.Seat', 'SEATS')

    @classmethod
    def get(cls, object_uuid):
        position = cache.get(object_uuid)
        if position is None:
            query = 'MATCH (p:`Position` {object_uuid:"%s"}) RETURN p' % \
                    object_uuid
            res, _ = db.cypher_query(query)
            if res.one:
                res.one.pull()
                position = Position.inflate(res.one)
                cache.set(object_uuid, position)
            else:
                position = None
        return position

    @classmethod
    def get_location(cls, object_uuid):
        location = cache.get("%s_location" % object_uuid)
        if location is None:
            query = 'MATCH (p:`Position` {object_uuid: "%s"})<-' \
                    '[:POSITIONS_AVAILABLE]-(c:`Location`) ' \
                    'RETURN c.object_uuid' % object_uuid
            res, col = db.cypher_query(query)
            try:
                location = res[0][0]
                cache.set("%s_location" % object_uuid, location)
            except IndexError:
                location = None
        return location

    @classmethod
    def get_location_name(cls, object_uuid):
        query = 'MATCH (p:Position {object_uuid: "%s"})<-' \
                '[:POSITIONS_AVAILABLE]-(location:Location) WITH p, location ' \
                'OPTIONAL MATCH (location)-[:ENCOMPASSED_BY]->' \
                '(location2:Location) ' \
                'RETURN location.name as first_name, ' \
                'location2.name as second_name' % object_uuid
        res, col = db.cypher_query(query)
        try:
            res = res[0]
            location = "%s, %s" % (res.first_name, res.second_name)
        except IndexError:
            location = None
        return location

    @classmethod
    def get_full_name(cls, object_uuid):
        """
        DEPRECATED
        Use the full_name attribute on the Position node itself instead.

        :param object_uuid:
        :return:
        """
        full_name = cache.get("%s_full_name" % object_uuid)
        if full_name is None:
            query = 'MATCH (p:Position {object_uuid: "%s"})<-' \
                    '[:POSITIONS_AVAILABLE]-(l:Location) WITH p, l ' \
                    'OPTIONAL MATCH (l:Location)-[:ENCOMPASSED_BY]->' \
                    '(l2:Location) WHERE l2.name<>"United States of ' \
                    'America" RETURN p.name as position_name, ' \
                    'l.name as location_name1, l2.name as location_name2, ' \
                    'p.level as position_level' \
                    % object_uuid
            res, _ = db.cypher_query(query)
            # position_name will be either 'House Representative', 'Senator',
            # 'State House Representative', or 'State Senator',
            #  location_name1 will be either a district number or a state name
            # and location_name2 will be a state name. This is done to build
            # up the full name of a position that a user can run for, we do
            # this because the query is set up the same for each different
            # query, for the senator we will get back a state name and a
            # string: "United States of America" and we don't want that
            # string included in the name but we also don't want to have to
            # do an if to determine what position we are looking at, it allows
            # for generalization of the query.
            try:
                if res[0][0] == 'House Representative' \
                        or res[0].position_level == "state_upper" \
                        or res[0].position_level == "state_lower":
                    full_name = "%s for %s's %s district" % \
                                (res[0].position_name, res[0].location_name2,
                                 ordinal(res[0].location_name1))
                else:
                    full_name = "%s of %s" % (res[0].position_name,
                                              res[0].location_name1)
                return {"full_name": full_name, "object_uuid": object_uuid}
            except IndexError:
                return None


class Seat(SBObject):
    # relationships
    position = RelationshipTo("sagebrew.sb_quests.neo_models.Position", "POSITION")
    current_holder = RelationshipTo("sagebrew.sb_quests.neo_models.PoliticalCampaign",
                                    "CURRENTLY_HELD_BY")
