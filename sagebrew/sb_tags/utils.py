from neomodel import db
from neomodel.exception import CypherException

from sb_base.decorators import apply_defense
from sb_tags.neo_models import Tag


@apply_defense
def create_tag_relations_util(tags):
    """
    This function creates and manages the relationships between tags, such as
    the frequently_tagged_with relationship.

    :param tags:
    :return:
    """
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

    except (CypherException, IOError) as e:
        return e


"""
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
            query = 'match (from: Tag {name: "%s"}), ' \
                    '(to: Tag {name: "%s"}) ,' \
                    'path = shortestPath(' \
                    '(to)-[:FREQUENTLY_TAGGED_WITH*]->(from))' \
                    'with ' \
                    'reduce(dist = 0, rel in rels(path) | dist + rel.count' \
                    ') as distance ' \
                    'return distance' % (tag.name, base_tag.name)
            db.cypher_query(query)
"""


def update_tags_util(tags):
    tag_list = []
    for name in tags:
        # This task should only ever be called after tags have been associated
        # with a user so the Tags should exist
        try:
            tag = Tag.nodes.get(name=name.lower())
            tag.tag_used += 1
            tag.save()
        except(CypherException, IOError) as e:
            return e
        tag_list.append(tag)

    for current_tag in tag_list:
        for tag in tag_list:
            if current_tag.name != tag.name:
                # TODO @Tyler need some assistance finalizing this
                # current_tag.frequently_used_with increment count
                # and should when should we be doing sphere calculation?
                pass

    return tags


def limit_offset_query(skip, limit):
    query = 'MATCH (tag:Tag) WHERE NOT tag:AutoTag ' \
                'RETURN tag SKIP %s LIMIT %s' % (skip, limit)
    res, _ = db.cypher_query(query)
    return [Tag.inflate(row[0]) for row in res]
