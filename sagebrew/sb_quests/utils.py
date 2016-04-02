from neomodel import db

from sb_quests.neo_models import Quest


def limit_offset_query(skip, limit):
    query = 'MATCH (quest:Quest) ' \
            'RETURN tag SKIP %s LIMIT %s' % (skip, limit)
    res, _ = db.cypher_query(query)
    return [Quest.inflate(row[0]) for row in res]
