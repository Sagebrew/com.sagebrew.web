from neomodel import (db, RelationshipTo, BooleanProperty, IntegerProperty,
                      StringProperty)

from sagebrew.api.neo_models import SBObject


class Donation(SBObject):
    """
    Donations are contributions made from one user to another. Initially this
    will be utilized solely to provide a way to store the donations between
    a user and a user waging a campaign. Eventually we will be utilizing this
    or a derivative of it to also help track donations made to groups, higher
    reputation users, and projects.

    If a user's donation goes over the amount needed for the goal and the
    campaigner is on their first goal or has provided an update on the
    previous goal we release all the funds pledged, we do not attempt to break
    them up. However any donations pledged after that release will result
    in the same process of not being released until the next goal threshold
    is crossed and an update has been provided.
    If a donation is provided that spans x goals then the representative
    will need to provide x updates prior to receiving their next release
    """
    # Whether or not the donation has been delivered or has just been pledged
    # False if Pledged and True if executed upon
    completed = BooleanProperty(default=False)
    # Set as a float to enable change to be specified. Even though from an
    # interface perspective we probably want to maintain that donations of
    # 5, 10, 100, etc are made.
    # Amount is an Integer to adhere to Stripe's API and to ensure precision
    # http://stackoverflow.com/questions/3730019/why-not-use-double-or-
    # float-to-represent-currency
    amount = IntegerProperty(required=True)
    # optimization
    owner_username = StringProperty()
    stripe_charge_id = StringProperty()
    mission_type = StringProperty()
    # Owner
    # Access who created this donation through:
    # Neomodel: donations Cypher: DONATIONS_GIVEN
    # RelationshipTo('plebs.neo_models.Pleb')

    # relationships
    mission = RelationshipTo(
        'sagebrew.sb_missions.neo_models.Mission', "CONTRIBUTED_TO")
    quest = RelationshipTo(
        'sagebrew.sb_quests.neo_models.Quest', "CONTRIBUTED_TO")

    # DEPRECATIONS
    # DEPRECATED: Rounds are deprecated and goals are no longer associated with
    # them. They are instead associated with Missions but are not aggregated
    # into rounds.
    owned_by = RelationshipTo('sagebrew.plebs.neo_models.Pleb', 'DONATED_FROM')

    @property
    def payment_method(self):
        # DO NOT USE: NON-USE PLACEHOLDER FOR SERIALIZER
        return None

    @classmethod
    def get_mission(cls, object_uuid):
        query = 'MATCH (d:Donation {object_uuid: "%s"})-' \
                '[:CONTRIBUTED_TO]->(mission:Mission) ' \
                'RETURN mission.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        return res[0][0] if res else None

    @classmethod
    def get_quest(cls, object_uuid):
        query = 'MATCH (d:Donation {object_uuid: "%s"})-' \
                '[:CONTRIBUTED_TO]->(mission:Mission)<-[:EMBARKS_ON]-' \
                '(quest:Quest) ' \
                'RETURN quest.object_uuid' % object_uuid
        res, _ = db.cypher_query(query)
        return res[0][0] if res else None

    @classmethod
    def get_owner(cls, object_uuid):
        query = 'MATCH (d:`Donation` {object_uuid: "%s"}) ' \
                'RETURN d.owner_username' % object_uuid
        res, col = db.cypher_query(query)
        try:
            return res[0][0]
        except IndexError:
            return None
