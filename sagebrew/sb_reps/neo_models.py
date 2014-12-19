from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException,
                      RelationshipFrom, DoesNotExist)

from plebs.neo_models import Pleb

class Bill(StructuredNode):
    bill_id = StringProperty(unique_index=True)

    #relationships
    proposer = RelationshipTo(BaseOfficial, "PROPOSED_BY")
    sponsor = RelationshipTo(BaseOfficial, "SPONSORED_BY")
    co_sponsor = RelationshipTo(BaseOfficial, "COSPONSORED_BY")

class Committee(StructuredNode):
    committee_number = IntegerProperty(unique_index=True)

    #relationships
    members = RelationshipTo(BaseOfficial, "COMMITEE_MEMBERS")

class Hearing(StructuredNode):
    hearing_id = StringProperty(unique_index=True)

    #relationships
    attendees = RelationshipTo(BaseOfficial, "HEARING_ATTENDEES")

class BaseOfficial(Pleb):
    sb_id = StringProperty(unique_index=True)

    #relationships
    pleb = RelationshipTo('plebs.neo_models.Pleb', 'IS')
    sponsored = RelationshipTo(Bill, "SPONSORED")
    co_sponsored = RelationshipTo(Bill, "COSPONSORED")
    proposed = RelationshipTo(Bill, "PROPOSED")
    hearings = RelationshipTo(Hearing, "ATTENDED")

class USSenator(BaseOfficial):
    #relationships
    committee = RelationshipTo(Committee, "PART_OF")


class Governor(BaseOfficial):
    vetoed = RelationshipTo(Bill, "VETOED")

class GovernorRequirements(StructuredNode):
    pass