import logging
from neomodel.exception import CypherException

from sb_base.decorators import apply_defense

logger = logging.getLogger('loggly_logs')

@apply_defense
def create_tag_relations_util(tags):
    '''
    This function creates and manages the relationships between tags, such as
    the frequently_tagged_with relationship.

    :param tags:
    :return:
    '''
    if not tags:
        return False

    try:
        for tag in tags:
            temp_list = tags
            temp_list.remove(tag)
            for item in temp_list:
                if tag.frequently_auto_tagged_with.is_connected(item):
                    rel = tag.frequently_auto_tagged_with.relationship(item)
                    rel.count += 1
                    rel.save()
                else:
                    rel = tag.frequently_auto_tagged_with.connect(item)
                    rel.save()
        return True

    except CypherException as e:
        return e


