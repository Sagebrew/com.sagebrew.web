from neomodel import (RelationshipTo)

from api.neo_models import SBObject


class Impression(SBObject):
    viewed_by = RelationshipTo('plebs.neo_models.Pleb', 'VIEWED_BY')
    viewed = RelationshipTo('sb_base.neo_models.VotableContent', 'VIEWED')
