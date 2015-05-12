from uuid import uuid1
from datetime import datetime
import pytz

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      BooleanProperty, DateTimeProperty,
                      JSONProperty, RelationshipTo)

from sb_search.neo_models import Searchable


class GTCongressNumbers(StructuredNode):
    congress_number = IntegerProperty(unique_index=True)


class GTPersonHistorical(StructuredNode):
    lastname = StringProperty()
    firstname = StringProperty()
    gender = StringProperty()
    legis_type = StringProperty()
    state = StringProperty()
    party = StringProperty()
    bioguideid = StringProperty()
    cspandid = IntegerProperty()
    gt_id = IntegerProperty(index=True)
    object_uuid = StringProperty(unique_index=True, default=uuid1)


class GTPerson(StructuredNode):
    bioguideid = StringProperty(default="")
    birthday = DateTimeProperty(default=datetime.now(pytz.utc))
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

    # relationships
    role = RelationshipTo('GTRole', 'HAS_A')
    votes = RelationshipTo('GT_RCVotes', 'HAS_A')
    committee = RelationshipTo('GTCommittee', 'IS_ON_A')


class GTRole(StructuredNode):
    current = BooleanProperty(index=True)
    description = StringProperty()
    district = IntegerProperty(index=True)
    enddate = DateTimeProperty(default=datetime.now(pytz.utc))
    role_id = IntegerProperty(unique_index=True)
    leadership_title = StringProperty()
    party = StringProperty(index=True)
    phone = StringProperty(index=True)
    role_type = StringProperty(index=True)
    role_type_label = StringProperty()
    senator_class = StringProperty()
    senator_class_label = StringProperty()
    senator_rank = StringProperty()
    senator_rank_label = StringProperty()
    startdate = DateTimeProperty(default=datetime.now(pytz.utc))
    state = StringProperty(index=True)
    title = StringProperty(index=True)
    title_long = StringProperty()
    website = StringProperty()

    person = RelationshipTo('GTPerson', "IS")
    congress_numbers = RelationshipTo('GTCongressNumbers', "PART_OF")


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

    # relationships
    option = RelationshipTo('GTVoteOption', 'HAS_A')


class GTCommittee(StructuredNode):
    abbrev = StringProperty()
    code = StringProperty()
    committee_id = IntegerProperty(unique_index=True)
    person = IntegerProperty()
    role = StringProperty()
    role_label = StringProperty()

    # relationships
    committee = RelationshipTo('GTCommittee', 'HAS_A_SUB')


class Term(Searchable):
    state = StringProperty()
    start = DateTimeProperty()
    end = DateTimeProperty()
    party = StringProperty()


class Senator(Term):
    senator_class = IntegerProperty()
    state_rank = StringProperty()


class HouseRepresentative(Term):
    district = IntegerProperty()
