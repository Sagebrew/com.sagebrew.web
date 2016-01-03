from django.core.cache import cache

from neomodel import (db, StringProperty, RelationshipTo, DoesNotExist,
                      BooleanProperty)

from sb_search.neo_models import Searchable
from sb_base.neo_models import VoteRelationship


class Mission(Searchable):
    """
    Missions are what a Quest is currently focused on doing. They encompass
    what it is trying to achieve whether it be running for office or advocating
    for something. A mission allows a Quest to take donations and for other
    Quests to endorse another Quest's missions.
    """
    # Whether the owner has taken the mission live or not. If the quest is not
    # live it will not show up as a donation option on the quest and will not
    # be selectable by normal users in any of the interfaces.
    active = BooleanProperty(default=False)
    # The owner is able to mark a mission as completed after it has started
    # this is basically saying the mission is over and they have either
    # succeeded or failed. The system can also mark political quests completed
    # upon election cycle completion. This fxn does not yet exist though
    completed = BooleanProperty(default=False)
    # TODO should be have people indicate if a mission was a success or a
    # failure?
    successful = BooleanProperty()
    about = StringProperty()
    epic = StringProperty()
    # Indicates what level the Mission is set at. Valid options are:
    #     state_upper
    #     state_lower
    #     state
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

    @classmethod
    def get_quest(cls, object_uuid):
        from sb_quests.neo_models import Quest
        return Quest.get(owner_username=Mission.get(
            object_uuid=object_uuid).owner_username)

    def get_focused_on(self, request=None):
        from api.neo_models import SBObject
        from sb_quests.neo_models import Position
        from sb_quests.serializers import PositionSerializer
        from sb_tags.neo_models import Tag
        from sb_tags.serializers import TagSerializer
        from sb_questions.neo_models import Question
        from sb_questions.serializers import QuestionSerializerNeo
        query = 'MATCH (a:Mission {object_uuid: "%s"})-[:FOCUSED_ON]->(b)' \
                'RETURN b' % self.object_uuid
        res, _ = db.cypher_query(query)
        if res.one:
            child_label = SBObject.inflate(res.one).get_child_label()
            if child_label == "Position":
                return PositionSerializer(Position.inflate(res.one),
                                          context={'request': request}).data
            elif child_label == "Tag":
                return TagSerializer(Tag.inflate(res.one),
                                     context={'request': request}).data
            elif child_label == "Question":
                return QuestionSerializerNeo(Question.inflate(res.one),
                                             context={'request': request}).data
        else:
            return None

    def get_location(self):
        from sb_locations.neo_models import Location
        query = 'MATCH (a:Mission {object_uuid: "%s"})' \
                '-[:WITHIN]->(b:Location) RETURN b' % self.object_uuid
        res, _ = db.cypher_query(query)
        if res.one:
            return Location.inflate(res.one)
        else:
            return None

    @classmethod
    def get_editors(cls, owner_username):
        from sb_quests.neo_models import Quest
        quest = Quest.get(owner_username)
        editors = cache.get("%s_editors" % quest.owner_username)
        if editors is None:
            query = 'MATCH (quest:Quest {owner_username: "%s")<-' \
                    '[:EDITOR_OF]-(pleb:pleb) ' \
                    'RETURN pleb.username' % quest
            res, col = db.cypher_query(query)
            editors = [row[0] for row in res]
            cache.set("%s_editors" % quest.owner_username, editors)
        return editors

    @classmethod
    def get_moderators(cls, owner_username):
        from sb_quests.neo_models import Quest
        quest = Quest.get(owner_username)
        moderators = cache.get("%s_moderators" % quest.owner_username)
        if moderators is None:
            query = 'MATCH (quest:Quest {owner_username: "%s")<-' \
                    '[:MODERATOR_OF]-(pleb:pleb) ' \
                    'RETURN pleb.username' % quest
            res, col = db.cypher_query(query)
            moderators = [row[0] for row in res]
            cache.set("%s_moderators" % quest.owner_username, moderators)
        return moderators

    def get_mission_title(self):
        if self.title:
            title = self.title
        else:
            if self.focus_name:
                title = self.focus_name.title().replace(
                    '-', ' ').replace('_', ' ')
            else:
                title = None
        return title
