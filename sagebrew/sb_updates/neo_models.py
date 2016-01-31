from neomodel import (db, RelationshipTo, StringProperty)

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
    mission = RelationshipTo('sb_missions.neo_models.Mission', "ABOUT")
    seat = RelationshipTo('sb_quests.neo_models.Seat', "ABOUT")
    quest = RelationshipTo('sb_quests.neo_models.Quest', "ABOUT")

    # Helper function that can be associated with the serializer and gets
    # the object the update is about.
    about = RelationshipTo('api.neo_models.SBObject', "ABOUT")

    # OPTIMIZATIONS
    about_id = StringProperty()
    # Valid Types Are:
    #    mission
    #    quest
    #    seat
    #    goal
    about_type = StringProperty()
