from django.core.cache import cache


from neomodel import (db, StringProperty, RelationshipTo, BooleanProperty,
                      DoesNotExist)

from sb_search.neo_models import Searchable


class Mission(Searchable):
    """
    """
    active = BooleanProperty(default=False)
    biography = StringProperty()
    epic = StringProperty()
    facebook = StringProperty()
    linkedin = StringProperty()
    youtube = StringProperty()
    twitter = StringProperty()
    website = StringProperty()
    # These are the wallpaper and profile specific to the campaign/action page
    # That way they have separation between the campaign and their personal
    # image.
    wallpaper_pic = StringProperty()
    # TODO do we need this? The mission is more about the cause than the person
    profile_pic = StringProperty()
    owner_username = StringProperty()
    # First and Last name are added to reduce potential additional queries
    # when rendering potential representative html to a users profile page
    title = StringProperty()

    # Optimizations
    position_name = StringProperty()
    location_name = StringProperty()
    position_formal_name = StringProperty()

    # Relationships
    donations = RelationshipTo('sb_donations.neo_models.Donation',
                               'RECEIVED_DONATION')
    goals = RelationshipTo('sb_goals.neo_models.Goal', "HAS_GOAL")

    updates = RelationshipTo('sb_updates.neo_models.Update', 'HAS_UPDATE')
    owned_by = RelationshipTo('sb_quests.neo_models.Campaign', 'WAGED_BY')

    position = RelationshipTo('sb_quests.neo_models.Position', 'RUNNING_FOR')
    # Utilized to link a Mission to a Question or Solution. Two use cases are
    # currently possible. One is that a parent Quest provides a solution or
    # Question and indicateds that it would like the given Mission to
    # be linked to that piece of content.
    #
    endorses = RelationshipTo('sb_base.neo_models.SBPublicContent', 'ENDORSES')

    @classmethod
    def get(cls, object_uuid):
        mission = cache.get("%s_mission" % object_uuid)
        if mission is None:
            query = 'MATCH (c:`Mission` {object_uuid: "%s"}) RETURN c' % \
                    object_uuid
            res, col = db.cypher_query(query)
            try:
                mission = cls.inflate(res[0][0])
                cache.set("%s_campaign" % object_uuid, mission)
            except IndexError:
                raise DoesNotExist("Quest does not exist")
        return mission
