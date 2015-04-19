from neomodel import CypherException, db

from sb_base.neo_models import VotableContent


def update_view_count(object_uuid):
    try:
        query = "MATCH (a:SBContent) WHERE a.object_uuid = " \
                "%s RETURN a" % (object_uuid)
        res, col = db.cypher_query(query)

        sb_object = VotableContent.inflate(res[0][0])
    except(CypherException, IOError) as e:
        return e
    sb_object.increment_view_count()

    return sb_object
