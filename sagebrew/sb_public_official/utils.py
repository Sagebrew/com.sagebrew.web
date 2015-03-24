import importlib
from dateutil import parser
from django.conf import settings
from neomodel import (DoesNotExist, CypherException)

from api.utils import spawn_task
from plebs.neo_models import Pleb
from .neo_models import Policy, BaseOfficial, Experience, Education, Goal
from sb_base.decorators import apply_defense

@apply_defense
def save_policy(rep_id, category, description, object_uuid):
    try:
        policy = Policy(category=category, description=description,
                        object_uuid=object_uuid).save()
    except CypherException as e:
        return e
    try:
        rep = BaseOfficial.nodes.get(object_uuid=rep_id)
    except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    try:
        rep.policy.connect(policy)
    except CypherException as e:
        return e
    return policy


@apply_defense
def save_experience(rep_id, title, start_date, end_date, current,
                         company, location, exp_id, description):
    try:
        exp = Experience.nodes.get(object_uuid=exp_id)
        return True
    except CypherException as e:
        return e
    except (Experience.DoesNotExist, DoesNotExist):
        try:
            rep = BaseOfficial.nodes.get(object_uuid=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
        try:
            experience = Experience(object_uuid=exp_id, title=title,
                                    start_date=start_date, end_date=end_date,
                                    current=current, company_s=company,
                                    location_s=location,
                                    description=description).save()
        except CypherException as e:
            return e
        try:
            rep.experience.connect(experience)
        except CypherException as e:
            return e
        return experience

@apply_defense
def save_education(rep_id, school, start_date, end_date, degree, edu_id):
    try:
        education = Education.nodes.get(object_uuid=edu_id)
        return True
    except CypherException as e:
        return e
    except (Education.DoesNotExist, DoesNotExist):
        try:
            rep = BaseOfficial.nodes.get(object_uuid=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
        try:
            education = Education(object_uuid=edu_id, school_s=school,
                                  end_date=end_date, start_date=start_date,
                                  degree=degree).save()
        except CypherException as e:
            return e
        try:
            rep.education.connect(education)
        except CypherException as e:
            return e
        return education

@apply_defense
def save_bio(rep_id, bio):
    try:
        rep = BaseOfficial.nodes.get(object_uuid=rep_id)
    except (CypherException, BaseOfficial.DoesNotExist, DoesNotExist) as e:
        return e
    try:
        rep.bio = bio
        rep.save()
    except CypherException as e:
        return e
    return bio

@apply_defense
def save_goal(rep_id, vote_req, money_req, initial, description, goal_id):
    try:
        goal = Goal.nodes.get(object_uuid=goal_id)
        return goal
    except CypherException as e:
        return e
    except (Goal.DoesNotExist, DoesNotExist):
        try:
            rep = BaseOfficial.nodes.get(object_uuid=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
        try:
            goal = Goal(object_uuid=goal_id, vote_req=vote_req, money_req=money_req,
                        initial=initial, description=description).save()
        except CypherException as e:
            return e
        try:
            rep.goal.connect(goal)
        except CypherException as e:
            return e
    return goal

def get_rep_type(rep_type):
    cls = rep_type
    module_name, class_name = cls.rsplit(".", 1)
    sb_module = importlib.import_module(module_name)
    sb_object = getattr(sb_module, class_name)
    return sb_object

@apply_defense
def save_rep(pleb_username, rep_type, rep_id, recipient_id, gov_phone,
             customer_id=None):
    try:
        pleb = Pleb.nodes.get(username=pleb_username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    temp_type = dict(settings.BASE_REP_TYPES)[rep_type]
    rep_type = get_rep_type(temp_type)
    try:
        rep = rep_type.nodes.get(object_uuid=rep_id)
    except CypherException as e:
        return e
    except (rep_type.DoesNotExist, DoesNotExist):
        rep = rep_type(object_uuid=rep_id, gov_phone=gov_phone).save()
    try:
        rep.pleb.connect(pleb)
        pleb.official.connect(rep)
        rep.save()
        pleb.save()
    except (CypherException, IOError) as e:
        return e
    try:
        rep.recipient_id = recipient_id
        if customer_id is not None:
            rep.customer_id = customer_id
        rep.save()
    except CypherException as e:
        return e
    return rep