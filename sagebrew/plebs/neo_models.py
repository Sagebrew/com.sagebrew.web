import pytz
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne,
                      CypherException, DoesNotExist)

from sb_relationships.neo_models import (FriendRelationship,
                                         UserWeightRelationship)
from sb_base.neo_models import RelationshipWeight
from sb_search.neo_models import SearchCount
from sb_tag.neo_models import SBTag


class TagRelationship(StructuredRel):
    total = IntegerProperty(default=0)
    rep_gained = IntegerProperty(default=0)
    rep_lost = IntegerProperty(default=0)


class PostObjectCreated(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    rep_gained = IntegerProperty(default=0)
    rep_lost = IntegerProperty(default=0)


class ActionActiveRel(StructuredRel):
    gained_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    active = BooleanProperty(default=True)
    lost_on = DateTimeProperty()


class RestrictionRel(StructuredRel):
    gained_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    active = BooleanProperty()


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
        'flag_as_other': -10, 'solutioned': 50, 'starred': 150, 'seen_search': 5,
        'seen_page': 20
    }
    gender = StringProperty()
    oauth_token = StringProperty()
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
    privileges = RelationshipTo('sb_privileges.neo_models.SBPrivilege', 'HAS',
                                model=ActionActiveRel)
    actions = RelationshipTo('sb_privileges.neo_models.SBAction', 'CAN',
                             model=ActionActiveRel)
    restrictions = RelationshipTo('sb_privileges.neo_models.SBRestriction',
                                  'RESTRICTED_BY', model=RestrictionRel)
    badges = RelationshipTo("sb_badges.neo_models.BadgeBase", "BADGES")
    oauth = RelationshipTo("plebs.neo_models.OauthUser", "OAUTH_CLIENT")
    tags = RelationshipTo('sb_tag.neo_models.SBTag', 'TAGS',
                          model=TagRelationship)
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
    #senator = RelationshipTo("govtrack.neo_models.GTRole",
    #                         "HAS_SENATOR")
    #house_rep = RelationshipTo("govtrack.neo_models.GTRole",
    #                           "HAS_REPRESENTATIVE")
    posts = RelationshipTo('sb_posts.neo_models.SBPost', 'OWNS_POST',
                           model=PostObjectCreated)
    questions = RelationshipTo('sb_questions.neo_models.SBQuestion',
                               'OWNS_QUESTION',
                               model=PostObjectCreated)
    solutions = RelationshipTo('sb_solutions.neo_models.SBSolution', 'OWNS_ANSWER',
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
    official = RelationshipTo('sb_public_official.neo_models.BaseOfficial', 'IS',
                              model=OfficialRelationship)

    def deactivate(self):
        return

    def get_restrictions(self):
        return self.restrictions.all()

    def get_actions(self):
        return self.actions.all()

    def get_privileges(self):
        return self.privileges.all()

    def get_badges(self):
        return self.badges.all()

    def get_full_name(self):
        return str(self.first_name) + " " + str(self.last_name)

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

    def get_owned_objects(self):
        return self.solutions.all()+self.questions.all()+\
               self.posts.all()+self.comments.all()

    def get_total_rep(self):
        rep_list = []
        base_tags = {}
        tags = {}
        total_rep = 0
        for item in self.get_owned_objects():
            rep_res = item.get_rep_breakout()
            total_rep += rep_res['total_rep']
            if 'base_tag_list' in rep_res.keys():
                for base_tag in rep_res['base_tag_list']:
                    base_tags[base_tag] = rep_res['rep_per_tag']
                for tag in rep_res['tag_list']:
                    tags[tag] = rep_res['rep_per_tag']
            rep_list.append(rep_res)
        return {"rep_list": rep_list,
                "base_tags": base_tags,
                "tags": tags,
                "total_rep": total_rep}

    def get_object_rep_count(self):
        pass

    def update_tag_rep(self, base_tags, tags):
        for item in tags:
            try:
                tag = SBTag.nodes.get(tag_name=item)
            except (SBTag.DoesNotExist, DoesNotExist, CypherException):
                continue
            if self.tags.is_connected(tag):
                rel = self.tags.relationship(tag)
                rel.total = tags[item]
                rel.save()
            else:
                rel = self.tags.connect(tag)
                rel.total = tags[item]
                rel.save()
        for item in base_tags:
            try:
                tag = SBTag.nodes.get(tag_name=item)
            except (SBTag.DoesNotExist, DoesNotExist, CypherException):
                continue
            if self.tags.is_connected(tag):
                rel = self.tags.relationship(tag)
                rel.total = base_tags[item]
                rel.save()
            else:
                rel = self.tags.connect(tag)
                rel.total = base_tags[item]
                rel.save()
        return True

    def get_conversation(self, expiry=0, now=0):
        return {"questions": [self.get_questions(expiry, now)],
                "solutions": [self.get_solutions(expiry, now)],
                "count": self.get_questions(expiry, now)['count']+\
                    self.get_solutions(expiry,now)['count']}

    def get_questions(self, expiry=0, now=0):
        if expiry == 0:
            return self.get_question_dicts(self.questions.all())
        return self.get_question_dicts(self.filter_questions(expiry, now))

    def get_solutions(self, expiry=0, now=0):
        if expiry == 0:
            return self.get_solution_dicts(self.solutions.all())
        return self.get_solution_dicts(self.filter_solutions(expiry, now))

    def get_solution_dicts(self, solutions):
        a_dict = {
            "solutions": []
        }
        for solution in solutions:
            a_dict['solutions'].append(solution.get_dict())
        a_dict['count'] = len(a_dict['solutions'])
        return a_dict

    def filter_solutions(self, expiry, now):
        solutions = []
        for solution in self.solutions.all():
            if (now-solution.created).seconds < expiry:
                solutions.append(solution)
        return solutions

    def filter_questions(self, expiry, now):
        questions = []
        for question in self.questions.all():
            if (now-question.created).seconds < expiry:
                questions.append(question)
        return questions

    # TODO Can we get rid of this now that we have an endpoint we can use?
    def get_question_dicts(self, questions):
        q_dict = {
            'questions': []
        }
        for question in questions:
            q_dict['questions'].append(question.get_single_dict())
        q_dict['count'] = len(q_dict['questions'])
        return q_dict

    def get_available_flags(self):
        pass

    def vote_on_content(self, content):
        pass

    def get_question_count(self):
        return len(self.questions.all())

    def get_solution_count(self):
        return len(self.solutions.all())

    def get_post_count(self):
        return len(self.posts.all())

    def get_comment_count(self):
        return len(self.comments.all())

    def get_friends(self):
        return self.friends.all()

    def get_friend_requests_sent(self):
        request_list = []
        for request in self.friend_requests_sent.all():
            try:
                request_list.append(request.request_to.all()[0].username)
            except IndexError:
                continue
        return request_list

    def determine_reps(self):
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


class OauthUser(StructuredNode):
    object_uuid = StringProperty(default=lambda: str(uuid1()))
    web_address = StringProperty(
        default=lambda: settings.WEB_ADDRESS+'/o/token/')
    access_token = StringProperty()
    expires_in = IntegerProperty()
    refresh_token = StringProperty()
    token_type = StringProperty(default="Bearer")
    last_modified = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class BetaUser(StructuredNode):
    email = StringProperty(unique_index=True)
    invited = BooleanProperty(default=False)
    signup_date = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

    def invite(self):
        from sb_registration.utils import sb_send_email
        if self.invited is True:
            return True
        self.invited = True
        self.save()
        template_dict = {
            "signup_url": "%s%s%s"%(settings.WEB_ADDRESS, "/signup/?user=",
                                    self.email)
        }
        html_content = get_template(
            'email_templates/email_beta_invite.html').render(
            Context(template_dict))
        sb_send_email("support@sagebrew.com", self.email, "Sagebrew Beta",
                      html_content)
        return True

