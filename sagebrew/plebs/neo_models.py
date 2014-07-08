from uuid import uuid1
from datetime import datetime
import pytz

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne)

from sb_wall.neo_models import SBWall
from govtrack.neo_models import GTRole

class PostObjectCreated(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

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
    district_name = StringProperty()
    school_name = StringProperty()
    phone_number = IntegerProperty()
    state = StringProperty()
    street = StringProperty()
    city = StringProperty()
    latitude = FloatProperty()
    longitude = FloatProperty()
    county = StringProperty()


class University(School):
    institution_name = StringProperty()
    univ_address = StringProperty()
    city = StringProperty()
    state = StringProperty()
    zipcode = StringProperty()
    chief_name = StringProperty()
    chief_title = StringProperty()
    website_url = StringProperty()
    admin_url = StringProperty()
    financial_url = StringProperty()
    app_url = StringProperty()
    county = StringProperty()
    longitude = FloatProperty()
    latitude = FloatProperty()



class ReceivedEducationRel(StructuredRel):
    started = DateTimeProperty()
    ended = DateTimeProperty()
    currently_attending = BooleanProperty()
    awarded = StringProperty()

class FriendRelationship(StructuredRel):
    since = DateTimeProperty()
    type = StringProperty(default="friends")


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
    reputation = IntegerProperty(default=0)

    # Relationships
    home_town_address = RelationshipTo("Address", "GREW_UP_AT")
    high_school = RelationshipTo("HighSchool", "ATTENDED", model=ReceivedEducationRel)
    university = RelationshipTo("University", "ATTENDED", model=ReceivedEducationRel)
    employer = RelationshipTo("Company", "WORKS_AT")
    address = RelationshipTo("Address", "LIVES_AT")
    topic_category = RelationshipTo("TopicCategory", "INTERESTED_IN")
    sb_topics = RelationshipTo("SBTopic", "INTERESTED_IN")
    friends = RelationshipTo("Pleb", "FRIENDS_WITH", model=FriendRelationship)
    senator = RelationshipTo("GTRole", "HAS_SENATOR")
    house_rep = RelationshipTo("GTRole", "HAS_REPRESENTATIVE")
    posts = RelationshipTo('sb_posts.neo_models.SBPost', 'OWNS', model=PostObjectCreated)
    comments = RelationshipTo('sb_comments.neo_models.SBComment', 'OWNS', model=PostObjectCreated)
    wall = RelationshipTo('sb_wall.neo_models.SBWall', 'OWNS')
    notifications = RelationshipTo('sb_notifications.neo_models.NotificationBase', 'RECIEVED_A')
    friend_requests_sent = RelationshipTo('sb_notifications.neo_models.FriendRequest', 'SENT_A_REQUEST')
    friend_requests_recieved = RelationshipTo('sb_notifications.neo_models.FriendRequest', 'RECIEVED_A_REQUEST')



class Address(StructuredNode):
    street = StringProperty()
    street_additional = StringProperty()
    city = StringProperty()
    state = StringProperty(index=True)
    postal_code = StringProperty()
    country = StringProperty()
    latitude = FloatProperty()
    longitude = FloatProperty()
    congressional_district = StringProperty()
    address_hash = StringProperty(unique_index=True)

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
        wall = SBWall(wall_id=uuid1())
        wall.save()
        wall.owner.connect(citizen)
        citizen.wall.connect(wall)
        wall.save()
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