from neomodel import (DoesNotExist, CypherException)

from .neo_models import Policy, BaseOfficial
from sb_base.decorators import apply_defense

@apply_defense
def save_policy(rep_id, category, description, object_uuid):
    try:
        policy = Policy(category=category, description=description,
                        sb_id=object_uuid).save()
    except CypherException as e:
        return e
    try:
        rep = BaseOfficial.nodes.get(sb_id=rep_id)
    except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    try:
        rep.policy.connect(policy)
    except CypherException as e:
        return e
    return policy


@apply_defense
def save_experience(rep_id, title, start_date, end_date, current,
                         company, location, exp_id, description):
    pass