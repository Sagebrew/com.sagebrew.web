import pytz
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    FloatProperty, BooleanProperty, DateProperty, DateTimeProperty,
    JSONProperty, AliasProperty, RelationshipTo, RelationshipFrom,
    Relationship)
from uuid import uuid1
from datetime import datetime

class GTRole(StructuredNode):
    congress_numbers = IntegerProperty()
    current = BooleanProperty()
    description = StringProperty()
    district = StringProperty()
    enddate = DateProperty()
    id = IntegerProperty(unique_index=True)
    leadership_title = StringProperty()
    party = StringProperty()
    phone = StringProperty()
    role_type = StringProperty()
    role_type_label = StringProperty()
    senator_class = StringProperty()
    senator_class_label = StringProperty()
    senator_rank = StringProperty()
    senator_rank_label = StringProperty()
    startdate = DateProperty()
    state = StringProperty()
    title = StringProperty()
    title_long = StringProperty()
    website = StringProperty()

class GTVotes(StructuredNode):
    aasdf = StringProperty()

class GTCommittee(StructuredNode):
    committee = IntegerProperty()
    id = IntegerProperty()
    person = IntegerProperty()
    role = StringProperty()
    role_label = StringProperty()

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
    role = RelationshipTo('GTRole','HAS_A')
    votes = RelationshipTo('GTVotes','HAS_A')
    committee = RelationshipTo('GTCommittee','IS_ON_A')



