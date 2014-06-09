from neomodel import StructuredNode,StringProperty, IntegerProperty, FloatProperty, BooleanProperty, DateProperty, DateTimeProperty, JSONProperty, AliasProperty, RelationshipTo, RelationshipFrom, Relationship

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
    bioguideid = StringProperty()
    birthday = DateProperty()
    cspanid = IntegerProperty()
    firstname = StringProperty()
    gender = StringProperty()
    gender_label = StringProperty()
    id = IntegerProperty(unique_index=True)
    lastname = StringProperty()
    link = StringProperty()
    middlename = StringProperty()
    name = StringProperty()
    namemod = StringProperty()
    nickname = StringProperty()
    osid = StringProperty()
    pvsid = IntegerProperty()
    sortname = StringProperty()
    twitterid = StringProperty()
    youtubeid = StringProperty()
    role = RelationshipTo('GTRole','HAS_A')
    votes = RelationshipTo('GTVotes','HAS_A')
    committee = RelationshipTo('GTCommittee','IS_ON_A')



