import shortuuid
from datetime import datetime
import pytz
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, db)

from sb_relationships.neo_models import (FriendRelationship,
                                         UserWeightRelationship)
from sb_posts.neo_models import RelationshipWeight
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
    email_verified = BooleanProperty(default=False)
    populated_es_index = BooleanProperty(default=False)
    populated_personal_index = BooleanProperty(default=False)
    initial_verification_email_sent = BooleanProperty(default=False)

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
    object_weight = RelationshipTo(['sb_questions.neo_models.SBQuestion',
                                   'sb_answers.neo_models.SBAnswer'],
                                   'OBJECT_WEIGHT',
                                   model=RelationshipWeight)
    searches = RelationshipTo('sb_search.neo_models.SearchQuery', 'SEARCHED',
                              model=SearchCount)
    clicked_results = RelationshipTo('sb_search.neo_models.SearchResult',
                                     'CLICKED_RESULT')

    def obj_weight_is_connected(self, obj):
        from sb_questions.neo_models import SBQuestion
        from sb_answers.neo_models import SBAnswer
        if obj.__class__ == SBQuestion:
            query = 'match (p:Pleb {email: "%s"})-[r:OBJECT_WEIGHT]->' \
                    '(s:SBQuestion {question_id: "%s"}) ' \
                    'return s' % (self.email, obj.question_id)
            res, meta = db.cypher_query(query)
            question = [SBQuestion.inflate(row[0]) for row in res]
            try:
                return question[0]
            except IndexError:
                return False

        elif obj.__class__ == SBAnswer:
            query = 'match (p:Pleb {email: "%s"})-[r:OBJECT_WEIGHT]->' \
                    '(s:SBAnswer {answer_id: "%s"}) ' \
                    'return s' % (self.email, obj.answer_id)
            res, meta = db.cypher_query(query)
            answer = [SBAnswer.inflate(row[0]) for row in res]
            try:
                return answer[0]
            except IndexError:
                return False

    def obj_weight_connect(self, obj):
        from sb_questions.neo_models import SBQuestion
        from sb_answers.neo_models import SBAnswer
        if obj.__class__ == SBQuestion:
            query = 'match (p:Pleb) where p.email="%s" with p match ' \
                    '(q:SBQuestion) where q.question_id="%s" ' \
                    'with p,q merge (p)-[r:OBJECT_WEIGHT]-(q) return r' % \
                    (self.email, obj.question_id)
            res, meta = db.cypher_query(query)
            rel = RelationshipWeight.inflate(res[0][0])
            if rel:
                return rel
            else:
                return False

        elif obj.__class__ == SBAnswer:
            query = 'match (p:Pleb) where p.email="%s" with p match ' \
                    '(a:SBAnswer) where a.answer_id="%s" ' \
                    'with p,a merge (p)-[r:OBJECT_WEIGHT]-(a) return r' % \
                    (self.email, obj.answer_id)
            res, meta = db.cypher_query(query)
            rel = RelationshipWeight.inflate(res[0][0])
            if res:
                return rel
            else:
                return False

    def obj_weight_relationship(self, obj):
        from sb_questions.neo_models import SBQuestion
        from sb_answers.neo_models import SBAnswer
        if obj.__class__ == SBQuestion:
            query = 'match (p:Pleb {email: "%s"})-[r:OBJECT_WEIGHT]->' \
                    '(q:SBQuestion {question_id: "%s"}) return r' % \
                    (self.email, obj.question_id)
            res, meta = db.cypher_query(query)
            rel = RelationshipWeight.inflate(res[0][0])
            return rel

        if obj.__class__ == SBAnswer:
            query = 'match (p:Pleb {email: "%s"})-[r:OBJECT_WEIGHT]->' \
                    '(a:SBAnswer {answer_id: "%s"}) return r' % \
                    (self.email, obj.answer_id)
            res, meta = db.cypher_query(query)
            rel = RelationshipWeight.inflate(res[0][0])
            return rel


    def generate_username(self):
        temp_username = str(self.first_name).lower() + \
                        str(self.last_name).lower()
        try:
            pleb = Pleb.nodes.get(username=temp_username)
            #TODO if first name and last name = the current one get a count of how many then add one
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
    validated = BooleanProperty(default=True)

    # Relationships
    address = RelationshipTo("Pleb", 'LIVES_IN')


class TopicCategory(StructuredNode):
    title = StringProperty(unique_index=True)
    description = StringProperty()
    sb_topics = RelationshipTo("SBTopic", "CONTAINS")


class SBTopic(StructuredNode):
    title = StringProperty(unique_index=True)
    description = StringProperty()
