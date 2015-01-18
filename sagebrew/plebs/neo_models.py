import re
import pytz
from datetime import datetime


from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne,
                      CypherException, DoesNotExist)

from api.utils import execute_cypher_query
from sb_relationships.neo_models import (FriendRelationship,
                                         UserWeightRelationship)
from sb_base.neo_models import RelationshipWeight
from sb_search.neo_models import SearchCount


class PostObjectCreated(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

class OfficialRelationship(StructuredRel):
    active = BooleanProperty(default=False)
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()

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
    search_modifiers = {
        'post': 10, 'comment_on': 5, 'upvote': 3, 'downvote': -3,
        'time': -1, 'proximity_to_you': 10, 'proximity_to_interest': 10,
        'share': 7, 'flag_as_inappropriate': -5, 'flag_as_spam': -100,
        'flag_as_other': -10, 'answered': 50, 'starred': 150, 'seen_search': 5,
        'seen_page': 20
    }
    username = StringProperty(unique_index=True, default=None)
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
    email_verified = BooleanProperty(default=False)
    populated_es_index = BooleanProperty(default=False)
    populated_personal_index = BooleanProperty(default=False)
    initial_verification_email_sent = BooleanProperty(default=False)
    search_id = StringProperty()
    stripe_customer_id = StringProperty()

    # Relationships
    voted_on = RelationshipTo('sb_base.neo_models.SBVoteableContent', 'VOTES')
    home_town_address = RelationshipTo("Address", "GREW_UP_AT")
    high_school = RelationshipTo("HighSchool", "ATTENDED_HS",
                                 model=ReceivedEducationRel)
    university = RelationshipTo("University", "ATTENDED_UNIV",
                                model=ReceivedEducationRel)
    employer = RelationshipTo("Company", "WORKS_AT")
    address = RelationshipTo("Address", "LIVES_AT", cardinality=ZeroOrOne)
    interests = RelationshipTo("sb_tag.neo_models.SBTag", "INTERESTED_IN")
    friends = RelationshipTo("Pleb", "FRIENDS_WITH", model=FriendRelationship)
    senator = RelationshipTo("govtrack.neo_models.GTRole",
                             "HAS_SENATOR")
    house_rep = RelationshipTo("govtrack.neo_models.GTRole",
                               "HAS_REPRESENTATIVE")
    posts = RelationshipTo('sb_posts.neo_models.SBPost', 'OWNS_POST',
                           model=PostObjectCreated)
    questions = RelationshipTo('sb_questions.neo_models.SBQuestion',
                               'OWNS_QUESTION',
                               model=PostObjectCreated)
    answers = RelationshipTo('sb_answers.neo_models.SBAnswer', 'OWNS_ANSWER',
                             model=PostObjectCreated)
    comments = RelationshipTo('sb_comments.neo_models.SBComment',
                              'OWNS_COMMENT',
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
    object_weight = RelationshipTo('sb_base.neo_models.SBContent',
                                   'OBJECT_WEIGHT',
                                   model=RelationshipWeight)
    searches = RelationshipTo('sb_search.neo_models.SearchQuery', 'SEARCHED',
                              model=SearchCount)
    clicked_results = RelationshipTo('sb_search.neo_models.SearchResult',
                                     'CLICKED_RESULT')
    official = RelationshipTo('sb_reps.neo_models.BaseOfficial', 'IS',
                              model=OfficialRelationship)

    def relate_comment(self, comment):
        try:
            rel_to_pleb = comment.is_owned_by.connect(self)
            rel_to_pleb.save()
            rel_from_pleb = self.comments.connect(comment)
            rel_from_pleb.save()
            return True
        except CypherException as e:
            return e

    def update_weight_relationship(self, sb_object, modifier_type):
        rel = self.object_weight.relationship(sb_object)
        if modifier_type in self.search_modifiers.keys():
            rel.weight += self.search_modifiers[modifier_type]
            rel.status = modifier_type
            rel.save()
            return rel.weight

    def get_available_flags(self):
        pass

    def vote_on_content(self, content):
        pass


class Address(StructuredNode):
    street = StringProperty()
    street_additional = StringProperty()
    city = StringProperty()
    state = StringProperty(index=True)
    postal_code = StringProperty(index=True)
    country = StringProperty()
    latitude = FloatProperty()
    longitude = FloatProperty()
    congressional_district = StringProperty()
    address_hash = StringProperty(unique_index=True)
    validated = BooleanProperty(default=True)

    # Relationships
    address = RelationshipTo("Pleb", 'LIVES_IN')

class Country(StructuredNode):
    name = StringProperty(unique_index=True)
    abbreviation = StringProperty()

    #relationships
    states = RelationshipTo('plebs.neo_models.State', 'HAS')

class State(StructuredNode):
    name = StringProperty(unique_index=True)
    abbreviation = StringProperty()

    #relationships
    capitol = RelationshipTo('plebs.neo_models.City', 'CAPITOL')

class County(StructuredNode):
    name = StringProperty()

    #relationships
    city = RelationshipTo('plebs.neo_models.City', "HAS")

class City(StructuredNode):
    name = StringProperty()

    #relationships
    district = RelationshipTo('plebs.neo_models.District', "RESIDES_IN")


class District(StructuredNode):
    number = IntegerProperty()
