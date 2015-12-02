from neomodel import (db, RelationshipTo)

from api.utils import deprecation
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
    # Updates should be focused on one of these things which is why we
    # are now using "ABOUT" for the relationship type for each of the
    # properties. This is because only one ABOUT relationship should
    # exist coming from an update.
    goal = RelationshipTo('sb_goals.neo_models.Goal', "ABOUT")
    mission = RelationshipTo('sb_mission.neo_models.Mission', "ABOUT")
    seat = RelationshipTo('sb_quests.neo_models.Seat', "ABOUT")

    # DEPRECATIONS
    # DEPRECATED: Goals are no longer the only thing that an update can be about
    # they may be about missions, seats, goals, etc. Updates should still be
    # focused on one of these things which is why we are now using "ABOUT" for
    # the relationship type for each of the properties. This is because only
    # one ABOUT relationship should exist coming from an update.
    goals = RelationshipTo('sb_goals.neo_models.Goal', "FOR_A")

    # DEPRECATED: This is an unnecessary relationship since the Quest already
    # has a relationship to the Update which can be used in all cases.
    # Access Quests (Campaigns) that are related to this Update through:
    # Neomodel: updates Cypher: HAS_UPDATE
    campaign = RelationshipTo('sb_quests.neo_models.Campaign', "ON_THE")

    @classmethod
    def get_goals(cls, object_uuid):
        query = 'MATCH (u:`Update` {object_uuid:"%s"})-[:FOR_A]-(g:`Goal`) ' \
                'RETURN g.object_uuid' % object_uuid
        res, col = db.cypher_query(query)
        return [row[0] for row in res]

    @classmethod
    def get_campaign(cls, object_uuid):
        deprecation("Quest references from the Campaign are deprecated. Please"
                    "query from the Campaign to the Quest.")
        query = 'MATCH (u:`Update` {object_uuid:"%s"})-[:ON_THE]-' \
                '(c:`Campaign`) RETURN c.object_uuid' % object_uuid
        res, col = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None
