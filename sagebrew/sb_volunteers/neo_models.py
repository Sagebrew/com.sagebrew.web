from neomodel import (StringProperty, RelationshipTo, ArrayProperty,
                      RelationshipFrom)

from sagebrew.api.neo_models import SBObject


class Volunteer(SBObject):
    # See VOLUNTEER_ACTIVITIES in settings for valid attributes that
    # can be placed within this property
    activities = ArrayProperty()

    # optimizations
    owner_username = StringProperty(index=True)
    mission_id = StringProperty()

    # relationships
    volunteer = RelationshipFrom('sagebrew.plebs.neo_models.Pleb', 'WANTS_TO')
    mission = RelationshipTo(
        'sagebrew.sb_missions.neo_models.Mission', 'ON_BEHALF_OF')
