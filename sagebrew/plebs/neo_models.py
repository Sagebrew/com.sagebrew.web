import shortuuid
from uuid import uuid1
from datetime import datetime
import pytz
from api.utils import spawn_task
from api.tasks import add_object_to_search_index
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty)

from sb_relationships.neo_models import FriendRelationship, UserWeightRelationship
from sb_posts.neo_models import RelationshipWeight
from sb_wall.neo_models import SBWall
from sb_search.neo_models import SearchCount


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


class Pleb(StructuredNode):
    username = StringProperty(unique_index=True)
    first_name = StringProperty()
    last_name = StringProperty()
    age = IntegerProperty()
    email = StringProperty(unique_index=True)
    date_of_birth = DateTimeProperty()
    primary_phone = StringProperty()
    secondary_phone = StringProperty()
    profile_pic = StringProperty()
    profile_pic_uuid = StringProperty()
    completed_profile_info = BooleanProperty(default=False)
    home_town = StringProperty()
    reputation = IntegerProperty(default=0)
    is_rep = BooleanProperty(default=False)
    is_admin = BooleanProperty(default=False)
    is_sage = BooleanProperty(default=False)
    search_index = StringProperty()
    base_index_id = StringProperty()

    # Relationships
    home_town_address = RelationshipTo("Address", "GREW_UP_AT")
    high_school = RelationshipTo("HighSchool", "ATTENDED_HS",
                                 model=ReceivedEducationRel)
    university = RelationshipTo("University", "ATTENDED_UNIV",
                                model=ReceivedEducationRel)
    employer = RelationshipTo("Company", "WORKS_AT")
    address = RelationshipTo("Address", "LIVES_AT")
    topic_category = RelationshipTo("TopicCategory", "INTERESTED_IN")
    sb_topics = RelationshipTo("SBTopic", "INTERESTED_IN")
    friends = RelationshipTo("Pleb", "FRIENDS_WITH", model=FriendRelationship)
    senator = RelationshipTo("govtrack.neo_models.GTRole",
                             "HAS_SENATOR")
    house_rep = RelationshipTo("govtrack.neo_models.GTRole",
                               "HAS_REPRESENTATIVE")
    posts = RelationshipTo('sb_posts.neo_models.SBPost', 'OWNS_POST',
                           model=PostObjectCreated)
    questions = RelationshipTo('sb_questions.neo_models.SBQuestion', 'OWNS_QUESTION',
                               model=PostObjectCreated)
    answers = RelationshipTo('sb_answers.neo_models.SBAnswer', 'OWNS_ANSWER',
                             model=PostObjectCreated)
    comments = RelationshipTo('sb_comments.neo_models.SBComment', 'OWNS_COMMENT',
                              model=PostObjectCreated)
    wall = RelationshipTo('sb_wall.neo_models.SBWall', 'OWNS_WALL')
    notifications = RelationshipTo(
        'sb_notifications.neo_models.NotificationBase', 'RECEIVED_A')
    friend_requests_sent = RelationshipTo(
        'sb_relationships.neo_models.FriendRequest', 'SENT_A_REQUEST')
    friend_requests_recieved = RelationshipTo(
        'sb_relationships.neo_models.FriendRequest', 'RECEIVED_A_REQUEST')
    user_weight = RelationshipTo('Pleb', 'WEIGHTED_USER',
                                 model=UserWeightRelationship)
    object_weight = RelationshipTo(['sb_questions.neo_models.SBQuestion',
                                    'sb_answers.neo_models.SBAnswer'],
                                     'OBJECT_WEIGHT',
                                     model=RelationshipWeight)
    searches = RelationshipTo('sb_search.neo_models.SearchQuery', 'SEARCHED',
                              model=SearchCount)
    clicked_results = RelationshipTo('sb_search.neo_models.SearchResult',
                                     'CLICKED_RESULT')

    def generate_username(self):
        temp_username = str(self.first_name).lower() + str(self.last_name).lower()
        try:
            pleb = Pleb.nodes.get(username=temp_username)
            self.username = shortuuid.ShortUUID()
            self.save()
        except Pleb.DoesNotExist:
            self.username = temp_username



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
    from sb_search.tasks import add_user_to_custom_index
    if created:
        # fixes test fails due to ghost plebs
        if instance.email == "":
            return None
        try:
            citizen = Pleb.nodes.get(email=instance.email)
        except Pleb.DoesNotExist:
            instance.username = str(shortuuid.uuid())
            instance.save()
            citizen = Pleb(email=instance.email,
                           first_name=instance.first_name,
                           last_name=instance.last_name)
            citizen.save()
            wall = SBWall(wall_id=uuid1())
            wall.save()
            wall.owner.connect(citizen)
            citizen.wall.connect(wall)
            wall.save()
            citizen.save()
            task_data = {'object_data': {
                'first_name': citizen.first_name,
                'last_name': citizen.last_name,
                'full_name': str(citizen.first_name) + ' '
                             + str(citizen.last_name),
                'pleb_email': citizen.email
                },
                         'object_type': 'pleb'
            }
            spawn_task(task_func=add_object_to_search_index,
                       task_param=task_data)
            task_data = {'pleb': citizen.email,
                         'index': "full-search-user-specific-1"}
            spawn_task(task_func=add_user_to_custom_index,
                       task_param=task_data)
    else:
        pass
        # citizen = Pleb.nodes.get(instance.email)
        # TODO may not be necessary but if we update an email or something
        # we need to remember to update it in the pleb instance and the
        # default django instance.
        # citizen.first_name = instance.firstname
        #citizen.last_name = instance.lastname


post_save.connect(create_user_profile, sender=User)
