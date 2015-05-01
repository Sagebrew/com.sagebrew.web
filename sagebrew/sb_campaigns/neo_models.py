from neomodel import (StringProperty, RelationshipTo, BooleanProperty,
                      IntegerProperty)

from sb_base.neo_models import (VoteRelationship)

from sb_search.neo_models import Searchable


class Campaign(Searchable):
    """
    Campaigns are basically a one to one with an action area, much like a Wall
    is with a profile page. The campaign stores all the relevant information
    that a user needs to have a Public page where they can accept donations
    towards either a more defined type of campaign such as a Political one or
    a more generalized such as a advocacy campaign trying to bring attention
    to a given issue or to a group of Projects headed up or organized by
    a given user.
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


class StateCampaign(PoliticalCampaign):
    """
    A state campaign is a political campaign being waged at the state level. An
    example of this would be a Senator race.
    """
    state = StringProperty()


class DistrictCampaign(StateCampaign):
    """
    A district campaign is a political campaign being waged at the district
    level. An example of this would be a House Representative race.
    """
    district = IntegerProperty()
