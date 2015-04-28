import pytz

from datetime import datetime

from django.conf import settings

from neomodel import (StringProperty, DateTimeProperty, RelationshipTo,
                      BooleanProperty, db, IntegerProperty)

from api.neo_models import SBObject
from sb_search.neo_models import Searchable


class Donation(SBObject):
    # Whether or not the donation has been delivered or has just been pledged
    # False if Pledged and True if executed upon
    completed = BooleanProperty(default=False)
    amount = IntegerProperty()

    # relationships
    campaign = RelationshipTo('sb_campaigns.neo_models.Campaign',
                              'DONATED_TO')
    # Donated for is what goal the user actually pledged the donation to.
    # Applied to are the goals the donation was actually applied to. This in
    # most circumstances will be the same goal as was donated for but may
    # cover multiple goals based on the donation amount.
    # If a user's donation goes over the amount needed for the goal and the
    # campaigner is on their first goal or has provided an update on the
    # previous goal we release all the funds pledged, we do not attempt to break
    # them up. However any donations pledged after that release will result
    # in the same process of not being released until the next goal threshold
    # is crossed and an update has been provided.
    # If a donation is provided that spans x goals then the representative
    # will need to provide x updates prior to receiving their next release
    donated_for = RelationshipTo('sb_goals.neo_models.Goal', 'DONATED_FOR')
    applied_to = RelationshipTo('sb_goals.neo_models.Goal', 'APPLIED_TO')
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'DONATED_FROM')