from neomodel import (StringProperty, RelationshipTo)

from sb_base.neo_models import VotableContent


class Flag(VotableContent):
    reputation_loss = 30
    flag_type = StringProperty()

    flag_on = RelationshipTo('sb_base.neo_models.SBContent', "FLAG_ON")
