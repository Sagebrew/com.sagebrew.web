from neomodel import (StringProperty)

from sb_base.neo_models import VoteRelationship


class CounselVote(VoteRelationship):
    reasoning = StringProperty()
