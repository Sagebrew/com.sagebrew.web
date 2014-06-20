from uuid import uuid1
import pytz

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)


class School(StructuredNode):
    name = StringProperty()
    address = RelationshipTo("Address", "LOCATED_AT")
    established = DateTimeProperty()
    population = IntegerProperty()

class Company(StructuredNode):
    name = StringProperty()
    address = RelationshipTo("Address", "LOCATED_AT")
    company_size = IntegerProperty()
    established = DateTimeProperty()
    industry = RelationshipTo("Industry", "PART_OF")


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
    completed_profile_info = BooleanProperty(default=False)
    home_town = StringProperty()

    # Relationships
    home_town_address = RelationshipTo("Address", "GREW_UP_AT")
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
    latitude = IntegerProperty()
    longitude = IntegerProperty()
    congressional_district = StringProperty()

    # Relationships
    address = RelationshipTo("Pleb", 'LIVES_IN')


class TopicCategory(StructuredNode):
    title = StringProperty(unique_index=True)
    description = StringProperty()
    sb_topics = RelationshipTo("SBTopic", "CONTAINS")


class SBTopic(StructuredNode):
    title = StringProperty(unique_index=True)
    description = StringProperty()



def create_user_profile(sender, instance, created, **kwargs):
    if created:
        citizen = Pleb(email=instance.email, first_name=instance.first_name,
                       last_name=instance.last_name)
        citizen.save()
    else:
        pass
        # citizen = Pleb.index.get(instance.email)
        # TODO may not be necessary but if we update an email or something
        # we need to remember to update it in the pleb instance and the
        # default django instance.
        #citizen.first_name = instance.firstname
        #citizen.last_name = instance.lastname


post_save.connect(create_user_profile, sender=User)