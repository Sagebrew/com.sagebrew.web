from sb_base.decorators import apply_defense

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, DateProperty)

from api.neo_models import SBObject
from plebs.neo_models import Pleb


class CongressVoteRelationship(StructuredRel):
    pass


class BaseOfficial(Pleb):
    type_str = "f46fbcda-9da8-11e4-9233-080027242395"
    title = StringProperty()
    bio = StringProperty(default="")
    name_mod = StringProperty()
    current = BooleanProperty()
    district = IntegerProperty(default=0)
    state = StringProperty()
    website = StringProperty()
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()
    full_name = StringProperty()
    gov_phone = StringProperty()
    # recipient_id and customer_id are stripe specific attributes
    recipient_id = StringProperty()
    customer_id = StringProperty()

    # relationships
    pleb = RelationshipTo('plebs.neo_models.Pleb', 'IS')
    sponsored = RelationshipTo('sb_public_official.neo_models.Bill',
                               "SPONSORED")
    co_sponsored = RelationshipTo('sb_public_official.neo_models.Bill',
                                  "COSPONSORED")
    proposed = RelationshipTo('sb_public_official.neo_models.Bill',
                              "PROPOSED")
    hearings = RelationshipTo('sb_public_official.neo_models.Hearing',
                              "ATTENDED")
    experience = RelationshipTo('sb_public_official.neo_models.Experience',
                                "EXPERIENCED")
    goal = RelationshipTo('sb_public_official.neo_models.Goal', 'GOAL')
    gt_person = RelationshipTo('govtrack.neo_models.GTPerson', 'GTPERSON')
    gt_role = RelationshipTo('govtrack.neo_models.GTRole', 'GTROLE')

    def get_dict(self):
        return {"object_uuid": self.object_uuid,
                "full_name": self.full_name,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "start_date": unicode(self.start_date),
                "end_date": unicode(self.end_date),
                "state": self.state,
                "title": self.title,
                "district": self.district,
                "current": self.current}


class Bill(StructuredNode):
    bill_id = StringProperty(unique_index=True)

    # relationships
    proposer = RelationshipTo(BaseOfficial, "PROPOSED_BY")
    sponsor = RelationshipTo(BaseOfficial, "SPONSORED_BY")
    co_sponsor = RelationshipTo(BaseOfficial, "COSPONSORED_BY")


class Hearing(StructuredNode):
    hearing_id = StringProperty(unique_index=True)

    # relationships
    attendees = RelationshipTo(BaseOfficial, "HEARING_ATTENDEES")


class Committee(StructuredNode):
    committee_number = IntegerProperty(unique_index=True)

    # relationships
    members = RelationshipTo(BaseOfficial, "COMMITTEE_MEMBERS")


class Experience(SBObject):
    title = StringProperty()
    start_date = DateProperty()
    end_date = DateProperty()
    description = StringProperty()
    current = BooleanProperty()
    company_s = StringProperty()
    location_s = StringProperty()

    # relationships
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


class Goal(SBObject):
    initial = BooleanProperty(default=False)
    description = StringProperty()
    vote_req = IntegerProperty()
    money_req = IntegerProperty()

    @apply_defense
    def get_dict(self):
        return {"object_uuid": self.object_uuid,
                "initial": self.initial,
                "description": self.description,
                "money_req": self.money_req,
                "vote_req": self.vote_req}
