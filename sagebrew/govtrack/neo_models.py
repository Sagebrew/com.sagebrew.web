from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    FloatProperty, BooleanProperty, DateProperty, DateTimeProperty,
    JSONProperty, AliasProperty, RelationshipTo, RelationshipFrom,
    Relationship)
from uuid import uuid1
from datetime import datetime
import pytz


class GTCongressNumbers(StructuredNode):
    congress_number = IntegerProperty(unique_index=True)

class GTRole(StructuredNode):
    current = BooleanProperty()
    description = StringProperty()
    district = StringProperty()
    enddate = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    role_id = IntegerProperty(unique_index=True)
    leadership_title = StringProperty()
    party = StringProperty()
    phone = StringProperty()
    role_type = StringProperty()
    role_type_label = StringProperty()
    senator_class = StringProperty()
    senator_class_label = StringProperty()
    senator_rank = StringProperty()
    senator_rank_label = StringProperty()
    startdate = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    state = StringProperty()
    title = StringProperty()
    title_long = StringProperty()
    website = StringProperty()

    congress_numbers = Relationship(GTCongressNumbers, "PART_OF")



class GTVoteOption(StructuredNode):
    option_id = IntegerProperty(unique_index=True)
    key = StringProperty(default="")
    value = StringProperty(index=True, default="")
    vote = IntegerProperty()


class GT_RCVotes(StructuredNode):
    category_one = StringProperty(default="")
    category_label = StringProperty(default="")
    chamber = StringProperty(default="")
    chamber_label = StringProperty(default="")
    congress = IntegerProperty()
    created = StringProperty(default="")
    vote_id = IntegerProperty(unique_index=True)
    link = StringProperty(default="")
    missing_data = BooleanProperty()
    number = IntegerProperty()
    question = StringProperty(default="")
    question_details = StringProperty(default="")
    related_amendment = IntegerProperty()
    related_bill = JSONProperty()
    required = StringProperty()
    result = StringProperty(default="")
    session = StringProperty(default="")
    source = StringProperty(default="")
    source_label = StringProperty(default="")
    total_minus = IntegerProperty()
    total_other = IntegerProperty()
    total_plus = IntegerProperty()
    vote_type = StringProperty(default="")

    #relationships
    option = Relationship('GTVoteOption','HAS_A')


class GTCommittee(StructuredNode):
    abbrev = StringProperty()
    code = StringProperty()
    committee_id = IntegerProperty(unique_index=True)
    person = IntegerProperty()
    role = StringProperty()
    role_label = StringProperty()

    #relationships
    committee = Relationship('GTCommittee','HAS_A_SUB')

class GTPerson(StructuredNode):
    bioguideid = StringProperty(default="")
    birthday = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    cspanid = IntegerProperty()
    firstname = StringProperty(default="")
    gender = StringProperty(default="")
    gender_label = StringProperty(default="")
    gt_id = IntegerProperty(unique_index=True)
    lastname = StringProperty(default="")
    link = StringProperty(default="")
    middlename = StringProperty(default="")
    name = StringProperty(default="")
    namemod = StringProperty(default="")
    nickname = StringProperty(default="")
    osid = StringProperty(default="")
    pvsid = IntegerProperty()
    sortname = StringProperty(default="")
    twitterid = StringProperty(default="")
    youtubeid = StringProperty(default="")

    #relationships
    role = RelationshipTo('GTRole','HAS_A')
    votes = RelationshipTo('GT_RCVotes','HAS_A')
    committee = RelationshipTo('GTCommittee','IS_ON_A')



