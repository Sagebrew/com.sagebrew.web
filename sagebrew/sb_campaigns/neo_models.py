from django.core.cache import cache

from rest_framework.reverse import reverse

from neomodel import (db, StringProperty, RelationshipTo, BooleanProperty)

from sb_base.neo_models import (VoteRelationship)
from sb_search.neo_models import Searchable, SBObject

from logging import getLogger
logger = getLogger('loggly_logs')


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
    potentially have a single Action Area defined that is specific to them but
    then either be leading or participating in a set of Projects. These
    projects may have different stripe accounts associated with them as they
    may be associated with different groups or bank accounts.

    In this case we could create a Campaign Node and add it to a new
    relationship property on a user called projects. The projects relationship
    could then bind 0-n projects to a user with a Relationship handler that
    indicated their role in the project. Then a user would still have a one
    to one with a Campaign and could also list the projects they wanted to
    on their Action Area while accepting donations directly to their primary
    Campaign, w/e it may be. This should make queries to do the population
    of such a Use Case pretty simple as well. We can also extend this class
    to a Project which may have some additional attributes but at a minimum
    would give us a Project Label to grab.

    The other case is if a user doesn't have an Action Area but owns or
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
    # Whether the account is in active or test/prep mode, once taken active
    # an account cannot be taken offline until the end of a campaign
    active = BooleanProperty(default=False)
    biography = StringProperty()
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

    # Relationships
    donations = RelationshipTo('sb_donations.neo_models.Donation',
                               'RECEIVED_DONATION')
    goals = RelationshipTo('sb_goals.neo_models.Goal', "HAS_GOAL")
    rounds = RelationshipTo('sb_goals.neo_models.Round', 'HAS_ROUND')
    updates = RelationshipTo('sb_updates.neo_models.Update', 'HAS_UPDATE')
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'WAGED_BY')
    # Will be an endpoint with the usernames of all the users that can edit
    # the page. That way we can easily check who has the right to modify
    # the page. These names should not be public
    editors = RelationshipTo('plebs.neo_models.Pleb', 'CAN_BE_EDITED_BY')
    accountants = RelationshipTo('plebs.neo_models.Pleb',
                                 'CAN_VIEW_MONETARY_DATA')
    position = RelationshipTo('sb_campaigns.neo_models.Position',
                              'RUNNING_FOR')

    @classmethod
    def get(cls, object_uuid):
        campaign = cache.get(object_uuid)
        if campaign is None:
            campaign = cls.nodes.get(object_uuid=object_uuid)
            cache.set(object_uuid, campaign)
        return campaign

    @classmethod
    def get_editors(cls, object_uuid):
        editors = cache.get("%s_editors" % (object_uuid))
        if editors is None:
            query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                    '[:CAN_BE_EDITED_BY]-(p:`Pleb`) RETURN p.username' \
                    % (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_editors" % (object_uuid), [])
                return []
            cache.set("%s_editors" % (object_uuid), res[0])
            editors = res[0]
        return editors

    @classmethod
    def get_accountants(cls, object_uuid):
        accountants = cache.get("%s_accountants" % (object_uuid))
        if accountants is None:
            query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                    '[:CAN_VIEW_MONETARY_DATA]-(p:`Pleb`) RETURN p.username' \
                    % (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_accountants" % (object_uuid), [])
                return []
            cache.set("%s_accountants" % (object_uuid), res[0])
            accountants = res[0]
        return accountants

    @classmethod
    def get_campaign_helpers(cls, object_uuid):
        return Campaign.get_accountants(object_uuid) + \
               Campaign.get_editors(object_uuid)

    @classmethod
    def get_url(cls, object_uuid, request):
        query = 'MATCH (c:`Campaign` {object_uuid:"%s"})-' \
                '[:WAGED_BY]-(p:`Pleb`) return p.username' % (object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return None
        return reverse('action_saga',
                       kwargs={"username": res[0][0]},
                       request=request)

    @classmethod
    def get_rounds(cls, object_uuid):
        rounds = cache.get("%s_rounds" % (object_uuid))
        if rounds is None:
            query = 'MATCH (c:`Campaign` {object_uuid: "%s"})-' \
                    '[:HAS_ROUND]->(r:`Round`) RETURN r.object_uuid' % \
                    (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_rounds" % (object_uuid), None)
                return res
            rounds = res[0]
            cache.set("%s_rounds" % (object_uuid), res[0])
        return rounds

    @classmethod
    def get_active_goals(cls, object_uuid):
        active_goals = cache.get("%s_active_goals" % (object_uuid))
        if active_goals is None:
            query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:HAS_ROUND]->" \
                    "(r:`Round`)-[:STRIVING_FOR]->(g:`Goal`) WHERE " \
                    "r.active=true RETURN g.object_uuid ORDER BY g.created" % \
                    (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_active_goals" % (object_uuid), None)
                return []
            active_goals = res[0]
            cache.set("%s_active_goals" % (object_uuid), active_goals)
        return active_goals

    @classmethod
    def get_active_round(cls, object_uuid):
        active_round = cache.get("%s_active_round" % (object_uuid))
        if active_round is None:
            query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:HAS_ROUND]->" \
                    "(r:`Round`) WHERE r.active=true RETURN r.object_uuid" % \
                    (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_active_round" % (object_uuid), None)
                return None
            active_round = res[0][0]
            cache.set("%s_active_round" % (object_uuid), active_round)
        return active_round

    @classmethod
    def get_updates(cls, object_uuid):
        updates = cache.get("%s_updates" % (object_uuid))
        if updates is None:
            query = 'MATCH (c:`Campaign` {object_uuid:"%s"})-[:HAS_UPDATE]-' \
                    '(u:`Update`) WHERE u.to_be_deleted=false ' \
                    'RETURN u.object_uuid' % (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_updates" % (object_uuid), None)
                return []
            updates = res[0]
            cache.set("%s_updates" % (object_uuid), updates)
        return updates

    @classmethod
    def get_position(cls, object_uuid):
        position = cache.get("%s_position" % (object_uuid))
        if position is None:
            query = "MATCH (r:`Campaign` {object_uuid:'%s'})-[:RUNNING_FOR]->" \
                    "(p:`Position`) RETURN p.object_uuid" % (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_position" % (object_uuid), None)
                return None
            position = res[0][0]
            cache.set("%s_position" % (object_uuid), position)
        return position


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

    @classmethod
    def get_vote_count(cls, object_uuid):
        query = 'MATCH (c:`PoliticalCampaign` {object_uuid:"%s"})-' \
                '[r:RECEIVED_PLEDGED_VOTE]->(p:`Pleb`) WHERE ' \
                'r.active=true RETURN count(r)' % (object_uuid)
        res, col = db.cypher_query(query)
        return res[0][0]

    @classmethod
    def get_constituents(cls, object_uuid):
        query = 'MATCH (c:`PoliticalCampaign` {object_uuid:"%s"})-' \
                '[r:POTENTIAL_REPRESENTATIVE_FOR]->(p:`Pleb`) ' \
                'RETURN p.username' % (object_uuid)
        res, col = db.cypher_query(query)
        if not res:
            return []
        return res[0]


class Position(SBObject):
    name = StringProperty()

    location = RelationshipTo('sb_locations.neo_models.Location',
                              'AVAILABLE_WITHIN')
    currently_held_by = RelationshipTo('sb_public_official.neo_models.'
                                       'PublicOfficial', "CURRENTLY_HELD_BY")
    # the campaigns relationship will be linked to all the campaigns currently
    # running for this position
    campaigns = RelationshipTo('sb_campaigns.neo_models.PoliticalCampaign',
                               "CAMPAIGNS")

    @classmethod
    def get_campaigns(cls, object_uuid):
        campaigns = cache.get("%s_campaigns" % (object_uuid))
        if campaigns is None:
            query = 'MATCH (p:`Position` {object_uuid: "%s"})-[:CAMPAIGNS]-' \
                    '(c:`PoliticalCampaign`) RETURN c.object_uuid' % (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_campaigns" % (object_uuid), None)
                return []
            campaigns = res[0]
            cache.set("%s_campaigns" % (object_uuid), campaigns)
        return campaigns

    @classmethod
    def get_location(cls, object_uuid):
        location = cache.get("%s_location" % (object_uuid))
        if location is None:
            query = 'MATCH (p:`Position` {object_uuid: "%s"})-' \
                    '[:AVAILABLE_WITHIN]-(c:`Location`) ' \
                    'RETURN c.object_uuid' % (object_uuid)
            res, col = db.cypher_query(query)
            if not res:
                cache.set("%s_location" % (object_uuid), None)
                return None
            location = res[0][0]
            cache.set("%s_location" % (object_uuid), location)
        return location