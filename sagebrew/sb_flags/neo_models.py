from neomodel import (StringProperty, RelationshipTo, IntegerProperty)

from sagebrew.sb_base.neo_models import VotableContent


class Flag(VotableContent):
    table = StringProperty(default='flags')
    reputation_loss = IntegerProperty(default=30)
    flag_type = StringProperty()

    flag_on = RelationshipTo('sagebrew.sb_base.neo_models.SBContent', "FLAG_ON")
