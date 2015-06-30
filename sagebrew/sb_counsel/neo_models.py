from neomodel import (StringProperty, StructuredNode, StructuredRel,
                      IntegerProperty)

from sb_base.neo_models import VoteRelationship


class CounselVote(VoteRelationship):
    reasoning = StringProperty()
