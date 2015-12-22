from django.contrib.humanize.templatetags.humanize import ordinal
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status

from neomodel import (db, StringProperty, RelationshipTo, BooleanProperty,
                      FloatProperty, DoesNotExist, RelationshipFrom)

from api.utils import deprecation
from sb_base.neo_models import (VoteRelationship)
from sb_search.neo_models import Searchable, SBObject


class Quest(Searchable):
    """
    A Quest is about the individual or group and tracking thier progress
    over the years. See Missions for their specific endeavours.
    """
    stripe_id = StringProperty(index=True, default="Not Set")
    stripe_customer_id = StringProperty()
    stripe_subscription_id = StringProperty()

    # Valid options are:
    #     free
    #     paid
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
    wallpaper_pic = StringProperty()
    profile_pic = StringProperty()
    application_fee = FloatProperty(default=0.041)
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

    # Relationships
    # Donations
    # Access Donations that are related to this Quest through:
    # Neomodel: quest Cypher: CONTRIBUTED_TO
    # RelationshipTo('sb_donations.neo_models.Donation')

    updates = RelationshipTo('sb_updates.neo_models.Update', 'CREATED_AN')

    # Pleb
    # Access the Pleb that owns this Quest through:
    # Neomodel: quest Cypher: IS_WAGING
    # RelationshipTo('sb_plebs.neo_models.Pleb')

    # Will be an endpoint with the usernames of all the users that can edit
    # the page. That way we can easily check who has the right to modify
    # the page. These names should not be public
    editors = RelationshipFrom('plebs.neo_models.Pleb', 'EDITOR_OF')
    moderators = RelationshipFrom('plebs.neo_models.Pleb', 'MODERATOR_OF')

    # Embarks on is a mission this Quest manages and is trying to accomplish.
    # Donations to these missions come back to the Quest's account
    missions = RelationshipTo('sb_missions.neo_models.Mission', "EMBARKS_ON")
    # Endorses are missions the Quest is supporting. These should be linked to
    # from the Quest page but are actively managed by other users/Quests.
    # Donations to these missions do not come back to this Quest.
    endorses = RelationshipTo('sb_missions.neo_models.Mission', "ENDORSES")
    holds = RelationshipTo('sb_quests.neo_models.Seat', "HOLDS")

    @property
    def ein(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def ssn(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def stripe_token(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def customer_token(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def routing_number(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @property
    def account_number(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @classmethod
    def get(cls, owner_username):
        campaign = cache.get("%s_quest" % owner_username)
        if campaign is None:
            query = 'MATCH (c:Quest {owner_username: "%s"}) RETURN c' % \
                    owner_username
            res, col = db.cypher_query(query)
            try:
                campaign = cls.inflate(res[0][0])
                cache.set("%s_quest" % owner_username, campaign)
                return campaign
            except IndexError:
                raise DoesNotExist("Quest does not exist")
        return campaign

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

    def get_public_official(self):
        """
        DEPRECATED
        :return:
        """
        from sb_public_official.neo_models import PublicOfficial
        public_official = cache.get("%s_public_official" % self.owner_username)
        if public_official is None:
            query = "MATCH (r:`Campaign` {object_uuid:'%s'})-" \
                    "[:HAS_PUBLIC_OFFICIAL]->(p:`PublicOfficial`) RETURN p" \
                    % self.owner_username
            res, _ = db.cypher_query(query)
            try:
                public_official = PublicOfficial.inflate(res[0][0])
                cache.set("%s_public_official" % self.owner_username,
                          public_official)
            except IndexError:
                public_official = None
        return public_official


class Campaign(Searchable):
    """
    Campaigns are basically a one to one with an action area, much like a Wall
    is with a profile page. The campaign stores all the relevant information
    that a user needs to have a Public page where they can accept donations
    towards either a more defined type of campaign such as a Political one or
    a more generalized such as a advocacy campaign trying to bring attention
    to a given issue or to a group of Projects headed up or organized by
    a given user.

    Use Case:
    How do we handle the future Projects feature with this? Users will
    potentially have a single Quest defined that is specific to them but
    then either be leading or participating in a set of Projects. These
    projects may have different stripe accounts associated with them as they
    may be associated with different groups or bank accounts.

    In this case we could create a Campaign Node and add it to a new
    relationship property on a user called projects. The projects relationship
    could then bind 0-n projects to a user with a Relationship handler that
    indicated their role in the project. Then a user would still have a one
    to one with a Campaign and could also list the projects they wanted to
    on their Quest while accepting donations directly to their primary
    Campaign, w/e it may be. This should make queries to do the population
    of such a Use Case pretty simple as well. We can also extend this class
    to a Project which may have some additional attributes but at a minimum
    would give us a Project Label to grab.

    The other case is if a user doesn't have a Quest but owns or
    participates in a Project. The above scenario should still work in this
    case as well.
    """

    # Inherits from SBPublicContent since eventually we'll probably want to be
    # able to do everything we do with Questions and Solutions to the campaign
    # content. Tag, Search, Vote, etc. Based on this we may want to move
    # content or Epic out to it's own node but this creates less queries

    # This should not be opened up to the serializer
    # This is only an index so that users don't have to assign it immediately
    # as they may not have it until after they've signed up.
    stripe_id = StringProperty(index=True, default="Not Set")
    stripe_customer_id = StringProperty()
    stripe_subscription_id = StringProperty()
    # Whether the account is in active or test/prep mode, once taken active
    # an account cannot be taken offline until the end of a campaign
    active = BooleanProperty(default=False)
    biography = StringProperty()
    epic = StringProperty()
    facebook = StringProperty()
    linkedin = StringProperty()
    youtube = StringProperty()
    twitter = StringProperty()
    website = StringProperty()
    # These are the wallpaper and profile specific to the campaign/action page
    # That way they have separation between the campaign and their personal
    # image.
    wallpaper_pic = StringProperty()
    profile_pic = StringProperty()
    owner_username = StringProperty()
    # First and Last name are added to reduce potential additional queries
    # when rendering potential representative html to a users profile page
    first_name = StringProperty()
    last_name = StringProperty()
    application_fee = FloatProperty(default=0.041)
    last_four_soc = StringProperty()

    # Optimizations
    location_name = StringProperty()
    # Seat name and formal name have taken the place of position and are for
    # storing the title of the seat a Quest currently holds.
    seat_name = StringProperty()
    seat_formal_name = StringProperty()

    # Relationships
    donations = RelationshipTo('sb_donations.neo_models.Donation',
                               'RECEIVED_DONATION')

    updates = RelationshipTo('sb_updates.neo_models.Update', 'HAS_UPDATE')
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'WAGED_BY')
    # Will be an endpoint with the usernames of all the users that can edit
    # the page. That way we can easily check who has the right to modify
    # the page. These names should not be public
    editors = RelationshipTo('plebs.neo_models.Pleb', 'CAN_BE_EDITED_BY')
    accountants = RelationshipTo('plebs.neo_models.Pleb',
                                 'CAN_VIEW_MONETARY_DATA')

    public_official = RelationshipTo(
        'sb_public_official.neo_models.PublicOfficial', 'HAS_PUBLIC_OFFICIAL')
    # Embarks on is a mission this Quest manages and is trying to accomplish.
    # Donations to these missions come back to the Quest's account
    missions = RelationshipTo('sb_missions.neo_models.Mission', "EMBARKS_ON")
    # Endorses are missions the Quest is supporting. These should be linked to
    # from the Quest page but are actively managed by other users/Quests.
    # Donations to these missions do not come back to this Quest.
    endorses = RelationshipTo('sb_missions.neo_models.Mission', "ENDORSES")

    # DEPRECATIONS
    # DEPRECATED: Rounds are now deprecated and should not be used
    rounds = RelationshipTo('sb_goals.neo_models.Round', 'HAS_ROUND')
    active_round = RelationshipTo('sb_goals.neo_models.Round',
                                  "CURRENT_ROUND")
    upcoming_round = RelationshipTo('sb_goals.neo_models.Round',
                                    "UPCOMING_ROUND")
    # DEPRECATED: Running for a position is now handled by an attached Mission
    position = RelationshipTo('sb_quests.neo_models.Position',
                              'RUNNING_FOR')
    position_formal_name = StringProperty()
    position_name = StringProperty()
    # DEPRECATED: Goals are now associated with Missions rather than the Quest
    # directly
    goals = RelationshipTo('sb_goals.neo_models.Goal', "HAS_GOAL")

    @classmethod
    def get(cls, object_uuid):
        campaign = cache.get("%s_campaign" % object_uuid)
        if campaign is None:
            query = 'MATCH (c:`Campaign` {object_uuid: "%s"}) RETURN c' % \
                    object_uuid
            res, col = db.cypher_query(query)
            try:
                campaign = cls.inflate(res[0][0])
                cache.set("%s_campaign" % object_uuid, campaign)
                return campaign
            except IndexError:
                raise DoesNotExist("Quest does not exist")
        return campaign

    @classmethod
    def get_editors(cls, object_uuid):
        editors = cache.get("%s_editors" % object_uuid)
        if editors is None:
            query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                    '[:CAN_BE_EDITED_BY]->(p:`Pleb`) RETURN p.username' % (
                        object_uuid)
            res, col = db.cypher_query(query)
            editors = [row[0] for row in res]
            cache.set("%s_editors" % object_uuid, editors)
        return editors

    @classmethod
    def get_accountants(cls, object_uuid):
        accountants = cache.get("%s_accountants" % object_uuid)
        if accountants is None:
            query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                    '[:CAN_VIEW_MONETARY_DATA]->(p:`Pleb`) RETURN p.username' \
                    % object_uuid
            res, col = db.cypher_query(query)
            accountants = [row[0] for row in res]
            cache.set("%s_accountants" % object_uuid, accountants)
        return accountants

    @classmethod
    def get_campaign_helpers(cls, object_uuid):
        return Campaign.get_accountants(object_uuid) + Campaign.get_editors(
            object_uuid)

    @classmethod
    def get_url(cls, object_uuid, request):
        query = 'MATCH (c:`Campaign` {object_uuid:"%s"})-' \
                '[:WAGED_BY]->(p:`Pleb`) return p.username' % object_uuid
        res, _ = db.cypher_query(query)
        try:
            return reverse('quest',
                           kwargs={"username": res.one},
                           request=request)
        except IndexError:
            return None

    @classmethod
    def get_rounds(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        rounds = cache.get("%s_rounds" % object_uuid)
        if rounds is None:
            query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                    '[:HAS_ROUND]->(r:`Round`) ' \
                    'WHERE r.active=false AND r.completed=null ' \
                    'RETURN r.object_uuid' % object_uuid
            res, col = db.cypher_query(query)
            rounds = [row[0] for row in res]
            cache.set("%s_rounds" % object_uuid, rounds)
        return rounds

    @classmethod
    def get_active_goals(cls, object_uuid):
        deprecation("Goals should no longer be attached directly to a Quest")
        active_goals = cache.get("%s_active_goals" % object_uuid)
        if active_goals is None:
            query = "MATCH (c:`Campaign` {object_uuid:'%s'})-" \
                    "[:CURRENT_ROUND]->(r:`Round`)-[:STRIVING_FOR]->" \
                    "(g:`Goal`) RETURN g.object_uuid ORDER BY g.created" % (
                        object_uuid)
            res, col = db.cypher_query(query)
            active_goals = [row[0] for row in res]
            cache.set("%s_active_goals" % object_uuid, active_goals)
        return active_goals

    @classmethod
    def get_active_round(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        active_round = cache.get("%s_active_round" % object_uuid)
        if active_round is None:
            query = "MATCH (c:`Campaign` {object_uuid:'%s'})-" \
                    "[:CURRENT_ROUND]->(r:`Round`) RETURN r.object_uuid" % \
                    object_uuid
            res, col = db.cypher_query(query)
            try:
                active_round = res[0][0]
                cache.set("%s_active_round" % object_uuid, active_round)
            except IndexError:
                active_round = None
        return active_round

    @classmethod
    def get_upcoming_round(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        upcoming_round = cache.get("%s_upcoming_round" % object_uuid)
        if upcoming_round is None:
            query = "MATCH (c:`Campaign` {object_uuid:'%s'})-" \
                    "[:UPCOMING_ROUND]->(r:`Round`) RETURN r.object_uuid" % \
                    object_uuid
            res, col = db.cypher_query(query)
            try:
                upcoming_round = res[0][0]
                cache.set("%s_upcoming_round" % object_uuid, upcoming_round)
            except IndexError:
                upcoming_round = None
        return upcoming_round

    @classmethod
    def get_updates(cls, object_uuid):
        updates = cache.get("%s_updates" % object_uuid)
        if updates is None:
            query = 'MATCH (c:`Campaign` {object_uuid:"%s"})-[:HAS_UPDATE]->' \
                    '(u:`Update`) WHERE u.to_be_deleted=false ' \
                    'RETURN u.object_uuid' % object_uuid
            res, col = db.cypher_query(query)
            updates = [row[0] for row in res]
            cache.set("%s_updates" % object_uuid, updates)
        return updates

    @classmethod
    def get_position(cls, object_uuid):
        deprecation("Positions are now linked to a Mission rather than "
                    "directly to the Quest")
        position = cache.get("%s_position" % object_uuid)
        if position is None:
            query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:RUNNING_FOR]->" \
                    "(p:`Position`) RETURN p.object_uuid" % object_uuid
            res, col = db.cypher_query(query)
            try:
                position = res[0][0]
                cache.set("%s_position" % object_uuid, position)
            except IndexError:
                position = None
        return position

    @classmethod
    def get_public_official(cls, object_uuid):
        from sb_public_official.neo_models import PublicOfficial
        public_official = cache.get("%s_public_official" % object_uuid)
        if public_official is None:
            query = "MATCH (r:`Campaign` {object_uuid:'%s'})-" \
                    "[:HAS_PUBLIC_OFFICIAL]->(p:`PublicOfficial`) RETURN p" \
                    % object_uuid
            res, _ = db.cypher_query(query)
            try:
                public_official = PublicOfficial.inflate(res[0][0])
                cache.set("%s_public_official" % object_uuid, public_official)
            except IndexError:
                public_official = None
        return public_official

    @classmethod
    def get_unassigned_goals(cls, object_uuid):
        from sb_goals.neo_models import Goal
        deprecation("Goals are now attached to Missions and should not be "
                    "associated directly with a Quest")
        query = 'MATCH (c:Campaign {object_uuid:"%s"})-[:HAS_GOAL]->' \
                '(g:Goal) WHERE NOT (g)-[:PART_OF]->(:Round) RETURN g ' \
                'ORDER BY g.monetary_requirement' % object_uuid
        res, _ = db.cypher_query(query)
        return [Goal.inflate(row[0]) for row in res]

    @classmethod
    def get_active_round_donation_total(cls, object_uuid):
        deprecation("Rounds are deprecated and should no longer be used.")
        query = 'MATCH (c:Campaign {object_uuid:"%s"})-[:CURRENT_ROUND]->' \
                '(r:Round)-[:HAS_DONATIONS]-(d:Donation) ' \
                'RETURN sum(d.amount)' % object_uuid
        res, _ = db.cypher_query(query)
        return res.one

    @classmethod
    def get_donations(cls, object_uuid):
        query = 'MATCH (c:Campaign {object_uuid:"%s"})-' \
                '[:RECEIVED_DONATION]->(d:Donation) RETURN d' % object_uuid
        res, _ = db.cypher_query(query)
        return [donation[0] for donation in res]

    @classmethod
    def get_possible_helpers(cls, object_uuid):
        query = 'MATCH (c:Campaign {object_uuid:"%s"})-[:WAGED_BY]->(p:Pleb)-' \
                '[:FRIENDS_WITH {active: true}]->' \
                '(b:Pleb) WHERE NOT (c)-[:CAN_BE_EDITED_BY]->(b) XOR ' \
                '(c)-[:CAN_VIEW_MONETARY_DATA]->(b) RETURN b.username' \
                % object_uuid
        res, _ = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def get_target_goal_donation_requirement(cls, object_uuid):
        deprecation("Goals are now attached to Missions and should not be "
                    "associated directly with a Quest")
        query = 'MATCH (c:Campaign {object_uuid:"%s"})-[:CURRENT_ROUND]->' \
                '(r:Round)-[:STRIVING_FOR]->(g:Goal {target:true}) ' \
                'RETURN g.total_required' \
                % object_uuid
        res, _ = db.cypher_query(query)
        return res.one

    @classmethod
    def get_target_goal_pledge_vote_requirement(cls, object_uuid):
        deprecation("Goals are now attached to Missions and should not be "
                    "associated directly with a Quest")
        query = 'MATCH (c:Campaign {object_uuid:"%s"})-[:CURRENT_ROUND]->' \
                '(r:Round)-[:STRIVING_FOR]->(g:Goal {target:true}) ' \
                'RETURN g.pledged_vote_requirement' % object_uuid
        res, _ = db.cypher_query(query)
        return res.one

    @classmethod
    def get_position_level(cls, object_uuid):
        deprecation("Positions are now linked to a Mission rather than "
                    "directly to the Quest")
        level = cache.get("%s_position_level" % object_uuid)
        if level is None:
            query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:RUNNING_FOR]->" \
                    "(p:`Position`) RETURN p.level" % object_uuid
            res, col = db.cypher_query(query)
            if res.one is not None:
                level = res.one
                cache.set("%s_position_level" % object_uuid, level)
        return level

    @classmethod
    def get_position_location(cls, object_uuid):
        deprecation("Positions are now linked to a Mission rather than "
                    "directly to the Quest")
        return Position.get_location(cls.get_position(object_uuid))

    @classmethod
    def get_total_donated(cls, object_uuid):
        total = cache.get("%s_total_donated" % object_uuid)
        if total is None:
            query = 'MATCH (r:`Campaign` {object_uuid:"%s"})-' \
                    '[:RECEIVED_DONATION]->(d:`Donation`) ' \
                    'RETURN sum(d.amount)' % object_uuid
            res, _ = db.cypher_query(query)
            if res.one is not None:
                total = res.one
                cache.set("%s_total_donated" % object_uuid, total)
        return total


class PoliticalCampaign(Campaign):
    """
    A political campaign is one where a user is running for public office. These
    campaigns are more strictly controlled and must follower certain legal
    parameters.
    """

    # city should be added when we can ascertain what cities are within the
    # district
    # addresses should be added when we can associate all the addresses within
    # the district
    # relationships

    # Using the `vote_on` property we could just associate the vote with the
    # campaign as we look at it just like another piece of content.
    pledged_votes = RelationshipTo('plebs.neo_models.Pleb',
                                   "RECEIVED_PLEDGED_VOTE",
                                   model=VoteRelationship)

    # This will be set differently for each of the different campaigns
    # For State we'll get the plebs living within the state and assign them
    # to this campaign. For District campaigns we'll filter on the district
    # and associate those users.
    # TODO should this be moved up to Campaign and be generalized to
    # those_affected?
    # Need to think about query on how we're going to display the senators,
    # reps, and presidents that can be voted on by the different users.
    constituents = RelationshipTo('plebs.neo_models.Pleb',
                                  'POTENTIAL_REPRESENTATIVE_FOR')

    # Seat
    # current_seat = RelationshipTo('sb_quests.neo_models.Seat', "CURRENT_SEAT")
    # Can access current_seat by using the relationship on seats:
    # CURRENTLY_HELD_BY going from the Seat to the Quest

    @classmethod
    def get(cls, object_uuid):
        campaign = cache.get("%s_campaign" % object_uuid)
        if campaign is None or type(campaign) is not PoliticalCampaign:
            query = 'MATCH (c:`PoliticalCampaign` {object_uuid: "%s"}) ' \
                    'RETURN c' % object_uuid
            res, col = db.cypher_query(query)
            try:
                campaign = PoliticalCampaign.inflate(res[0][0])
                cache.set("%s_campaign" % object_uuid, campaign)
                return campaign
            except IndexError:
                raise DoesNotExist("Quest does not exist")
        return campaign

    @classmethod
    def get_vote_count(cls, object_uuid):
        query = 'MATCH (c:`PoliticalCampaign` {object_uuid:"%s"})-' \
                '[r:RECEIVED_PLEDGED_VOTE]->(p:`Pleb`) WHERE ' \
                'r.active=true RETURN count(r)' % object_uuid
        res, col = db.cypher_query(query)
        try:
            vote_count = res[0][0]
            cache.set("%s_vote_count" % object_uuid, vote_count)
            return vote_count
        except IndexError:
            return None

    @classmethod
    def get_constituents(cls, object_uuid):
        query = 'MATCH (c:`PoliticalCampaign` {object_uuid:"%s"})-' \
                '[r:POTENTIAL_REPRESENTATIVE_FOR]->(p:`Pleb`) ' \
                'RETURN p.username' % object_uuid
        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def vote_campaign(cls, object_uuid, username):
        from plebs.neo_models import Pleb
        query = 'MATCH (c:PoliticalCampaign {object_uuid:"%s"})-' \
                '[r:RECEIVED_PLEDGED_VOTE]->(p:Pleb {username:"%s"}) ' \
                'RETURN r' % (object_uuid, username)
        res, _ = db.cypher_query(query)
        vote_relation = res.one
        if not vote_relation:
            pleb = Pleb.get(username=username)
            campaign = PoliticalCampaign.get(object_uuid=object_uuid)
            rel = campaign.pledged_votes.connect(pleb)
            rel.save()
            return True
        rel = VoteRelationship.inflate(vote_relation)
        if rel.active:
            rel.active = False
        else:
            rel.active = True
        rel.save()
        return rel.active

    @classmethod
    def get_allow_vote(cls, object_uuid, username):
        from plebs.neo_models import Pleb
        from sb_registration.utils import calc_age
        try:
            pleb = Pleb.get(username)
        except (Pleb.DoesNotExist, DoesNotExist):
            return False, {"detail": "This user does not exist.",
                           "status_code": status.HTTP_404_NOT_FOUND}
        if not pleb.is_verified:
            return False, {"detail": "You must be a verified user to pledge a "
                                     "vote to a Quest.",
                           "status_code": status.HTTP_401_UNAUTHORIZED}
        if calc_age(pleb.date_of_birth) < 18:
            return False, {"detail": "You must be at 18 years of age or older "
                                     "to pledge a vote to a Quest.",
                           "status_code": status.HTTP_401_UNAUTHORIZED}
        address = pleb.get_address()
        position = PoliticalCampaign.get_position(object_uuid)

        if position is None or address is None:
            return False, {"detail": "Either your address or the position of "
                                     "the Quest is invalid.",
                           "status_code": status.HTTP_400_BAD_REQUEST}
        # This query attempts to match a given position and address via
        # location connections, the end result is ensuring that someone
        # who does not live in a location that a quest is running in may
        # not pledge a vote for them.
        res, _ = db.cypher_query(
            'MATCH (p:`Position` {object_uuid: "%s"})-'
            '[:AVAILABLE_WITHIN]->(l1:Location)<-[t:ENCOMPASSED_BY*..]-'
            '(a:Address {object_uuid:"%s"}) RETURN t' % (
                position, address.object_uuid))

        if res.one:
            return True, {"detail": "Can pledge vote to this Quest.",
                          "status_code": status.HTTP_200_OK}
        return False, {"detail": "You cannot pledge vote to Quest outside "
                                 "your area.",
                       "status_code": status.HTTP_401_UNAUTHORIZED}

    @classmethod
    def get_current_seat(cls, object_uuid):
        query = 'MATCH (c:PoliticalCampaign {object_uuid:"%s"})-' \
                '[:CURRENTLY_HELD_SEAT]->(s:Seat) RETURN s.object_uuid' \
                % object_uuid
        res, _ = db.cypher_query(query)
        return res.one

    def pledged_votes_per_day(self):
        query = 'MATCH (c:PoliticalCampaign {object_uuid:"%s"})-' \
                '[r:RECEIVED_PLEDGED_VOTE]->(:Pleb) RETURN r ' \
                'ORDER BY r.created' \
                % self.object_uuid
        res, _ = db.cypher_query(query)
        vote_data = {}
        for vote in res:
            rel = VoteRelationship.inflate(vote[0])
            active_value = int(rel.active)
            date_string = rel.created.strftime('%Y-%m-%d')
            if date_string not in vote_data.keys():
                vote_data[date_string] = active_value
            else:
                vote_data[date_string] += active_value
        return vote_data


class Position(SBObject):
    name = StringProperty()
    full_name = StringProperty()
    # Valid Levels:
    #     state_upper - State Senator Districts
    #     state_lower - State House Representative Districts
    #     federal - U.S. Federal Districts (House of Reps)
    #     local - Everything else :)
    level = StringProperty(default="federal")

    location = RelationshipTo('sb_locations.neo_models.Location',
                              'AVAILABLE_WITHIN')
    currently_held_by = RelationshipTo('sb_public_official.neo_models.'
                                       'PublicOfficial', "CURRENTLY_HELD_BY")
    # the campaigns relationship will be linked to all the campaigns currently
    # running for this position
    campaigns = RelationshipTo('sb_quests.neo_models.PoliticalCampaign',
                               "CAMPAIGNS")
    restrictions = RelationshipTo('sb_privileges.neo_models.Restriction',
                                  'RESTRICTED_BY')
    seats = RelationshipTo('sb_quests.neo_models.Seat', 'SEATS')

    @classmethod
    def get(cls, object_uuid):
        position = cache.get(object_uuid)
        if position is None:
            query = 'MATCH (p:`Position` {object_uuid:"%s"}) RETURN p' % \
                    object_uuid
            res, col = db.cypher_query(query)
            try:
                position = Position.inflate(res[0][0])
                cache.set(object_uuid, position)
            except IndexError:
                position = None
        return position

    @classmethod
    def get_campaigns(cls, object_uuid):
        campaigns = cache.get("%s_campaigns" % object_uuid)
        if campaigns is None:
            query = 'MATCH (p:`Position` {object_uuid: "%s"})-[:CAMPAIGNS]->' \
                    '(c:`PoliticalCampaign`) RETURN c.object_uuid' % \
                    object_uuid
            res, col = db.cypher_query(query)
            campaigns = [row[0] for row in res]
            cache.set("%s_campaigns" % object_uuid, campaigns)
        return campaigns

    @classmethod
    def get_location(cls, object_uuid):
        location = cache.get("%s_location" % object_uuid)
        if location is None:
            query = 'MATCH (p:`Position` {object_uuid: "%s"})-' \
                    '[:AVAILABLE_WITHIN]->(c:`Location`) ' \
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
        query = 'MATCH (p:Position {object_uuid: "%s"})-' \
                '[:AVAILABLE_WITHIN]->(location:Location) ' \
                'RETURN location.name' % object_uuid
        res, col = db.cypher_query(query)
        try:
            location = res[0][0]
        except IndexError:
            location = None
        return location

    @classmethod
    def get_full_name(cls, object_uuid):
        '''
        DEPRECATED
        Use the full_name attribute on the Position node itself instead.

        :param object_uuid:
        :return:
        '''
        full_name = cache.get("%s_full_name" % object_uuid)
        if full_name is None:
            query = 'MATCH (p:Position {object_uuid: "%s"})-' \
                    '[:AVAILABLE_WITHIN]->(l:Location) WITH p, l ' \
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
    position = RelationshipTo("sb_quests.neo_models.Position", "POSITION")
    current_holder = RelationshipTo("sb_quests.neo_models.PoliticalCampaign",
                                    "CURRENTLY_HELD_BY")
