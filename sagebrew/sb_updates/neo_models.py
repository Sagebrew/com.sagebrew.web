from neomodel import (db, RelationshipTo)

from sb_base.neo_models import TitledContent


class Update(TitledContent):
    """
    Updates can be made on campaigns to provide a general update on the campaign
    or on a particular goal. We'd like campaigners to provide a specific update
    on the progress of a given goal as to ensure they are actually spending time
    on a goal rather than trying to cut corners and provide updates on multiple.
    This may change over time as reps want to associate an update with multiple
    goals after their initial one has been provided.
    Need to determine how that would be handled. Right now the model is future
    proof and doesn't care whether there is one or many goals associated with
    an update. So it is up to the frontend to determine how this should be
    implemented.
    """
    # relationships
    campaign = RelationshipTo('sb_campaigns.neo_models.Campaign',
                              "ON_THE")
    goals = RelationshipTo('sb_goals.neo_models.Goal', "FOR_A")

    @classmethod
    def get_goals(cls, object_uuid):
        query = 'MATCH (u:`Update` {object_uuid:"%s"})-[:FOR_A]-(g:`Goal`) ' \
                'RETURN g.object_uuid' % (object_uuid)
        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def get_campaign(cls, object_uuid):
        query = 'MATCH (u:`Update` {object_uuid:"%s"})-[:ON_THE]-' \
                '(c:`Campaign`) RETURN c.object_uuid' % (object_uuid)
        res, col = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None
