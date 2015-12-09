from django.core.cache import cache


from neomodel import (db, StringProperty, RelationshipTo, DoesNotExist)

from sb_search.neo_models import Searchable
from sb_base.neo_models import VoteRelationship


class Mission(Searchable):
    """
    Missions are what a Quest is currently focused on doing. They encompass
    what it is trying to achieve whether it be running for office or advocating
    for something. A mission allows a Quest to take donations and for other
    Quests to endorse another Quest's missions.
    """
    biography = StringProperty()
    epic = StringProperty()
    # Indicates what level the Mission is set at. Valid options are:
    #     state_upper
    #     state_lower
    #     federal
    #     local
    # For filtering purposes we combine state_upper and state_lower into "state"
    level = StringProperty()

    # The mission may have seperate pages than the core Quest does
    facebook = StringProperty()
    linkedin = StringProperty()
    youtube = StringProperty()
    twitter = StringProperty()
    website = StringProperty()

    # Allow the mission to have it's own wallpaper and a title
    wallpaper_pic = StringProperty()
    title = StringProperty()

    # Optimizations
    owner_username = StringProperty()
    location_name = StringProperty()

    # Used to store off what one thing the mission is focused on. This eases
    # the inflation, handling, etc of the focused on object
    # Valid options are:
    #     position
    #     advocacy
    focus_on_type = StringProperty()

    # If this is a political campaign these would be the title of the position
    # for tags these are the human readable versions of the tag. For Question
    # they are the title.
    focus_name = StringProperty()
    focus_formal_name = StringProperty()

    # Relationships
    goals = RelationshipTo('sb_goals.neo_models.Goal', "WORKING_TOWARDS")

    # Donations
    # Access Donations that are related to this Mission through:
    # Neomodel: mission Cypher: CONTRIBUTED_TO
    # RelationshipTo('sb_donations.neo_models.Donation')

    # Updates
    # Access Updates that are related to this Mission through:
    # Neomodel: mission Cypher: ABOUT
    # RelationshipFrom('sb_updates.neo_models.Update')

    # Quest - Owner
    # Access the Quest that manages this Mission:
    # Neomodel: missions Cypher: EMBARKS_ON
    # RelationshipFrom('sb_updates.neo_models.Campaign')

    # Each mission must be focused on achieving something. Whether it be to
    # obtain a position, advocate/help with an issue in an area (tag), or
    # solve a question. A mission should only ever have one of the following.
    # Since we create our own queries this shouldn't be an issue and is why
    # we use "FOCUSED_ON" for each of the items.
    position = RelationshipTo('sb_quests.neo_models.Position', 'FOCUSED_ON')
    tag = RelationshipTo('sb_tags.neo_models.Tag', 'FOCUSED_ON')
    question = RelationshipTo('sb_questions.neo_models.Question', 'FOCUSED_ON')

    # Helper function that can be associated with on the serializer and gets
    # a focused on object.
    focused_on = RelationshipTo('sb_search.neo_models.Searchable', 'FOCUSED_ON')

    # Utilized to link a Mission to a Question or Solution. Two use cases are
    # currently possible. One is that a parent Quest provides a solution or
    # Question and indicates that it would like the given Mission to
    # be linked to that piece of content.
    associated_with = RelationshipTo('sb_base.neo_models.SBPublicContent',
                                     'ASSOCIATED_WITH')
    # The place where this Mission is taking place. If it is of type position
    # then the location can also be queried through the position but since
    # there are multiple nodes such as tags and questions that can be the
    # focus we've added this to have a consistent way to query it. Theoretically
    # we could standardize verbage between tags, questions, and positions
    # in relation to locations but tags might be associated with multiple
    # locations.
    location = RelationshipTo('sb_locations.neo_models.Location', "WITHIN")

    # DEPRECATED
    # Pledge votes are from old campaigns. We're working on a new process
    # for this
    pledge_votes = RelationshipTo('plebs.neo_models.Pleb',
                                  'RECEIVED_PLEDGED_VOTE',
                                  model=VoteRelationship)

    @classmethod
    def get(cls, object_uuid):
        mission = cache.get("%s_mission" % object_uuid)
        if mission is None:
            query = 'MATCH (c:`Mission` {object_uuid: "%s"}) RETURN c' % \
                    object_uuid
            res, col = db.cypher_query(query)
            try:
                mission = cls.inflate(res[0][0])
                cache.set("%s_mission" % object_uuid, mission)
            except IndexError:
                raise DoesNotExist("Quest does not exist")
        return mission

    def get_focused_on(self):
        from api.neo_models import SBObject
        from sb_quests.neo_models import Position
        from sb_quests.serializers import PositionSerializer
        from sb_tags.neo_models import Tag
        from sb_tags.serializers import TagSerializer
        from sb_questions.neo_models import Question
        from sb_questions.serializers import QuestionSerializerNeo
        query = 'MATCH (a:Mission {object_uuid: "%s"})-[FOCUSED_ON]->(b)' \
                'RETURN b' % self.object_uuid
        res, _ = db.cypher_query(query)
        if res.one:
            child_label = SBObject.inflate(res.one).get_child_label()
            if child_label == "Position":
                return PositionSerializer(Position.inflate(res.one)).data
            elif child_label == "Tag":
                return TagSerializer(Tag.inflate(res.one)).data
            elif child_label == "Question":
                return QuestionSerializerNeo(Question.inflate(res.one)).data

    def get_location(self):
        from sb_locations.neo_models import Location
        query = 'MATCH (a:Mission {object_uuid: "%s"})' \
                '-[:WITHIN]->(b:Location) RETURN b' % self.object_uuid
        res, _ = db.cypher_query(query)
        if res.one:
            return Location.inflate(res.one)
        else:
            return None
