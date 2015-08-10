from neomodel import (StringProperty, RelationshipTo)

from api.neo_models import SBObject


class Badge(SBObject):
    name = StringProperty()
    image_color = StringProperty()
    image_grey = StringProperty()

    # relationships
    requirements = RelationshipTo('sb_requirements.neo_models.Requirement',
                                  "REQUIRES")


class BadgeGroup(SBObject):
    name = StringProperty()
    description = StringProperty()

    # relationships
    badges = RelationshipTo('sb_badges.neo_models.Badge', "HAS")
