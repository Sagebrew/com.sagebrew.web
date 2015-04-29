import pytz

from datetime import datetime

from neomodel import (StringProperty, RelationshipTo,
                      BooleanProperty, IntegerProperty)

from sb_base.neo_models import SBPublicContent
from sb_search.neo_models import Searchable


def get_current_time():
    return datetime.now(pytz.utc)


class Campaign(SBPublicContent, Searchable):
    # Inherits from SBPublicContent since eventually we'll probably want to be
    # able to do everything we do with Questions and Solutions to the campaign
    # content. Tag, Search, Vote, etc. Based on this we may want to move
    # content or Epic out to it's own node but this creates less queries

    # This should not be opened up to the serializer
    stripe_id = BooleanProperty(default=False)
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

    # city should be added when we can ascertain what cities are within the
    # district
    # addresses should be added when we can associate all the addresses within
    # the district
    # relationships
    donations = RelationshipTo('sb_donations.neo_models.Donation',
                               'RECEIVED_DONATION')
    goals = RelationshipTo('sb_goals.neo_models.Goal', "HAS_GOAL")
    # Using the `vote_on` property we could just associate the vote with the
    # campaign as we look at it just like another piece of content.
    pledged_votes = RelationshipTo('sb_votes.neo_models.CampaignVote',
                                   "RECEIVED_PLEDGED_VOTE")
    rounds = RelationshipTo('sb_goals.neo_models.Round', 'HAS_ROUND')
    updates = RelationshipTo('sb_updates.neo_models.Update', 'HAS_UPDATE')
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'WAGED_BY')
    # Will be an endpoint with the usernames of all the users that can edit
    # the page. That way we can easily check who has the right to modify
    # the page. These names should not be public
    editors = RelationshipTo('plebs.neo_models.Pleb', 'CAN_BE_EDITED_BY')
    accountants = RelationshipTo('plebs.neo_models.Pleb',
                                 'CAN_VIEW_MONETARY_DATA')
    # This will be set differently for each of the different campaigns
    # For State we'll get the plebs living within the state and assign them
    # to this campaign. For District campaigns we'll filter on the district
    # and associate those users.
    constituents = RelationshipTo('plebs.neo_models.Pleb',
                                  'POTENTIAL_REPRESENTATIVE_FOR')


class StateCampaign(Campaign):
    state = StringProperty()


class DistrictCampaign(StateCampaign):
    district = IntegerProperty()
