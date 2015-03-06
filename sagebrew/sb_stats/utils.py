from neomodel import CypherException

from api.utils import get_object
from sb_stats.neo_models import SBViewCount

def update_view_count(object_type, object_uuid):
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception):
        return sb_object
    try:
        view_count = SBViewCount().save()
    except (CypherException, IOError) as e:
        return e
    try:
        sb_object.view_count_node.connect(view_count)
    except (CypherException, IOError) as e:
        return e
    return True