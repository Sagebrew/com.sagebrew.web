from uuid import uuid1

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist)

from plebs.neo_models import Pleb


class CongressVoteRelationship(StructuredRel):
    pass

class BaseOfficial(Pleb):
    title = ""
    sb_id = StringProperty(unique_index=True)
    resume = StringProperty()
    agenda = StringProperty()
    policies = StringProperty()

    #relationships
    policy = RelationshipTo('sb_reps.neo_models.Policy', "HAS_POLICY")
    pleb = RelationshipTo('plebs.neo_models.Pleb', 'IS')
    sponsored = RelationshipTo('sb_reps.neo_models.Bill', "SPONSORED")
    co_sponsored = RelationshipTo('sb_reps.neo_models.Bill', "COSPONSORED")
    proposed = RelationshipTo('sb_reps.neo_models.Bill', "PROPOSED")
    hearings = RelationshipTo('sb_reps.neo_models.Hearing', "ATTENDED")
    experience = RelationshipTo('sb_reps.neo_models.Experience', "EXPERIENCED")

class Bill(StructuredNode):
    bill_id = StringProperty(unique_index=True)

    #relationships
    proposer = RelationshipTo(BaseOfficial, "PROPOSED_BY")
    sponsor = RelationshipTo(BaseOfficial, "SPONSORED_BY")
    co_sponsor = RelationshipTo(BaseOfficial, "COSPONSORED_BY")

class Hearing(StructuredNode):
    hearing_id = StringProperty(unique_index=True)

    #relationships
    attendees = RelationshipTo(BaseOfficial, "HEARING_ATTENDEES")

class USSenator(BaseOfficial):
    title = "Senator "
    is_majority_leader = BooleanProperty(default=False)
    is_minority_leader = BooleanProperty(default=False)

    #relationships
    committee = RelationshipTo('sb_reps.neo_models.Committee', "PART_OF")

class USPresident(BaseOfficial):
    title = "President "
    number = IntegerProperty()

    #relationships
    vetoed = RelationshipTo(Bill, "VETOED")

class Policy(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()))
    category = StringProperty()
    description = StringProperty()

class USHouseRepresentative(BaseOfficial):
    title = "Representative "
    seat = IntegerProperty(unique_index=True)
    is_speaker = BooleanProperty(default=False)
    is_majority_leader = BooleanProperty(default=False)
    is_minority_leader = BooleanProperty(default=False)

    #relationships
    vote = RelationshipTo('sb_reps.neo_models.Bill', 'VOTED_ON',)


class Committee(StructuredNode):
    committee_number = IntegerProperty(unique_index=True)

    #relationships
    members = RelationshipTo(BaseOfficial, "COMMITEE_MEMBERS")

class Governor(BaseOfficial):
    #relationships
    vetoed = RelationshipTo(Bill, "VETOED")
    passed = RelationshipTo(Bill, "PASSED")
    committee = RelationshipTo('sb_reps.neo_models.Committee', "STARTED")

class PositionRequirements(StructuredNode):
    position = StringProperty(unique_index=True)
    age = IntegerProperty()
    res_of_state = BooleanProperty(default=True)
    citizen_years = IntegerProperty()
    cannot_be_felon = BooleanProperty(default=True)
    registered_to_vote = BooleanProperty()
    registered_to_vote_years = IntegerProperty()
    natural_born_resident = BooleanProperty(default=False)
    term_limit = IntegerProperty()

class Experience(StructuredNode):
    title = StringProperty()
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()
    description = StringProperty()

    #relationships
    company = RelationshipTo('plebs.neo_models.Company', 'EXPERIENCED_AT')
    location = RelationshipTo('plebs.neo_models.Address', "LOCATION")