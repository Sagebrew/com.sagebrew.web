from uuid import uuid1
from sb_base.decorators import apply_defense

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist, DateProperty)

from plebs.neo_models import Pleb


class CongressVoteRelationship(StructuredRel):
    pass

class BaseOfficial(Pleb):
    title = StringProperty()
    type_str = "f46fbcda-9da8-11e4-9233-080027242395"
    sb_id = StringProperty(unique_index=True, default=str(uuid1()))
    bio = StringProperty(default="")
    recipient_id = StringProperty()
    customer_id = StringProperty()
    name_mod = StringProperty()
    current = BooleanProperty()
    district = IntegerProperty()
    state = StringProperty()
    website = StringProperty()
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()
    full_name = StringProperty()

    #relationships
    policy = RelationshipTo('sb_reps.neo_models.Policy', "HAS_POLICY")
    pleb = RelationshipTo('plebs.neo_models.Pleb', 'IS')
    sponsored = RelationshipTo('sb_reps.neo_models.Bill', "SPONSORED")
    co_sponsored = RelationshipTo('sb_reps.neo_models.Bill', "COSPONSORED")
    proposed = RelationshipTo('sb_reps.neo_models.Bill', "PROPOSED")
    hearings = RelationshipTo('sb_reps.neo_models.Hearing', "ATTENDED")
    experience = RelationshipTo('sb_reps.neo_models.Experience', "EXPERIENCED")
    education = RelationshipTo('sb_reps.neo_models.Education', 'EDUCATION')
    goal = RelationshipTo('sb_reps.neo_models.Goal', 'GOAL')
    gt_person = RelationshipTo('govtrack.neo_models.GTPerson', 'GTPERSON')
    gt_role = RelationshipTo('govtrack.neo_models.GTRole', 'GTROLE')

    def get_dict(self):
        return {"object_uuid": self.sb_id,
                "full_name": self.full_name,
                "start_date": unicode(self.start_date),
                "end_date": unicode(self.end_date),
                "state": self.state,
                "district": self.district,
                "current": self.current}


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
    type_str = "f2729db2-9da8-11e4-9233-080027242395"
    is_majority_leader = BooleanProperty(default=False)
    is_minority_leader = BooleanProperty(default=False)

    #relationships
    committee = RelationshipTo('sb_reps.neo_models.Committee', "PART_OF")

class USPresident(BaseOfficial):
    title = "President "
    type_str = "f3aeebe0-9da8-11e4-9233-080027242395"
    number = IntegerProperty()

    #relationships
    vetoed = RelationshipTo(Bill, "VETOED")

class Policy(StructuredNode):
    sb_id = StringProperty(default=lambda: str(uuid1()))
    category = StringProperty()
    description = StringProperty()

    @apply_defense
    def get_dict(self):
        return {"category": self.category,
                "description": self.description}

class USHouseRepresentative(BaseOfficial):
    title = "Representative "
    type_str = "628c138a-9da9-11e4-9233-080027242395"
    seat = IntegerProperty(unique_index=True)
    is_speaker = BooleanProperty(default=False)
    is_majority_leader = BooleanProperty(default=False)
    is_minority_leader = BooleanProperty(default=False)

    #relationships
    vote = RelationshipTo('sb_reps.neo_models.Bill', 'VOTED_ON',)


class Committee(StructuredNode):
    committee_number = IntegerProperty(unique_index=True)

    #relationships
    members = RelationshipTo(BaseOfficial, "COMMITTEE_MEMBERS")

class Governor(BaseOfficial):
    title = "Governor "
    type_str = "786dcf40-9da9-11e4-9233-080027242395"

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
    sb_id = StringProperty(unique_index=True)
    title = StringProperty()
    start_date = DateProperty()
    end_date = DateProperty()
    description = StringProperty()
    current = BooleanProperty()
    company_s = StringProperty()
    location_s = StringProperty()

    #relationships
    company = RelationshipTo('plebs.neo_models.Company', 'EXPERIENCED_AT')
    location = RelationshipTo('plebs.neo_models.Address', "LOCATION")

    @apply_defense
    def get_dict(self):
        return {"title": self.title,
                "start_date": unicode(self.start_date),
                "end_date": unicode(self.end_date),
                "description": self.description,
                "current": self.current,
                "company": self.company_s,
                "location": self.location_s}

class Education(StructuredNode):
    sb_id = StringProperty(unique_index=True)
    school_s = StringProperty()
    start_date = DateProperty()
    end_date = DateProperty()
    degree = StringProperty()

    #relationships
    school = RelationshipTo('plebs.neo_models.School', 'SCHOOL')

    @apply_defense
    def get_dict(self):
        return {"object_uuid": self.sb_id,
                "start_date": unicode(self.start_date),
                "end_date": unicode(self.end_date),
                "school": self.school_s,
                "degree": self.degree}

class Goal(StructuredNode):
    sb_id = StringProperty(unique_index=True)
    initial = BooleanProperty(default=False)
    description = StringProperty()
    vote_req = IntegerProperty()
    money_req = IntegerProperty()

    @apply_defense
    def get_dict(self):
        return {"object_uuid": self.sb_id,
                "initial": self.initial,
                "description": self.description,
                "money_req": self.money_req,
                "vote_req": self.vote_req}
