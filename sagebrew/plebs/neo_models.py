from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

from uuid import uuid1
from datetime import datetime
import pytz

class School(StructuredNode):
    address = RelationshipTo("Address", "LOCATED_AT")
    established = DateTimeProperty()
    population = IntegerProperty()


class HighSchool(School):
    pass


class University(School):
    pass


class ReceivedEducationRel(StructuredRel):
    started = DateTimeProperty()
    ended = DateTimeProperty()
    currently_attending = BooleanProperty()
    awarded = StringProperty()


class Pleb(StructuredNode):
    first_name = StringProperty()
    last_name = StringProperty()
    age = IntegerProperty()
    email = StringProperty(unique_index=True)
    date_of_birth = DateTimeProperty()
    primary_phone = StringProperty()
    secondary_phone = StringProperty()
    profile_pic = StringProperty()

    # Relationships
    home_town = RelationshipTo("Address", "GREW_UP_AT")
    high_school = RelationshipTo("HighSchool", "ATTENDED", model=ReceivedEducationRel)
    university = RelationshipTo("University", "ATTENDED", model=ReceivedEducationRel)
    employer = RelationshipTo("Company", "WORKS_AT")
    address = RelationshipTo("Address", "LIVES_AT")
    topic_category = RelationshipTo("TopicCategory", "INTERESTED_IN")
    sb_topics = RelationshipTo("SBTopic", "INTERESTED_IN")
    friends = RelationshipTo("Pleb", "FRIENDS_WITH")


class Address(StructuredNode):
    street = StringProperty()
    street_additional = StringProperty()
    city = StringProperty()
    state = StringProperty()
    postal_code = StringProperty()
    country = StringProperty()

    # Relationships
    address = RelationshipTo("Pleb", 'LIVES_IN')


class TopicCategory(StructuredNode):
    title = StringProperty()
    description = StringProperty()
    sb_topics = RelationshipTo("SBTopic", "CONTAINS")


class SBTopic(StructuredNode):
    title = StringProperty
    description = StringProperty()


