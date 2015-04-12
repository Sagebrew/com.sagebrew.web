import logging
from neomodel.exception import CypherException

from sb_base.decorators import apply_defense
from api.utils import execute_cypher_query
from sb_tag.neo_models import Tag

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
                if tag.frequently_tagged_with.is_connected(item):
                    rel = tag.frequently_tagged_with.relationship(item)
                    rel.count += 1
                    rel.save()
                else:
                    rel = tag.frequently_tagged_with.connect(item)
                    rel.save()
        return True

    except CypherException as e:
        return e


@apply_defense
def calc_spheres():
    tags = Tag.nodes.all()
    base_tags = []
    for index, tag in enumerate(tags):
        if tag.base:
            base_tags.append(tag)
            tags.pop(index)
    for tag in tags:
        for base_tag in base_tags:
            query = 'match (from: Tag {tag_name: "%s"}), ' \
                    '(to: Tag {tag_name: "%s"}) ,' \
                    'path = shortestPath((to)-[:FREQUENTLY_TAGGED_WITH*]->(from))' \
                    'with reduce(dist = 0, rel in rels(path) | dist + rel.count) as distance ' \
                    'return distance'%(tag.tag_name, base_tag.tag_name)
            res = execute_cypher_query(query)