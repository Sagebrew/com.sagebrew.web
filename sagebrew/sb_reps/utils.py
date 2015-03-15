import importlib
from django.conf import settings
from neomodel import (DoesNotExist, CypherException)

from api.utils import spawn_task, execute_cypher_query
from plebs.neo_models import Pleb
from .neo_models import Policy, BaseOfficial, Experience, Education, Goal
from sb_base.decorators import apply_defense

@apply_defense
def save_policy(rep_id, category, description, object_uuid):
    try:
        policy = Policy(category=category, description=description,
                        sb_id=object_uuid).save()
    except CypherException as e:
        return e
    try:
        rep = BaseOfficial.nodes.get(sb_id=rep_id)
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
        exp = Experience.nodes.get(sb_id=exp_id)
        return True
    except CypherException as e:
        return e
    except (Experience.DoesNotExist, DoesNotExist):
        try:
            rep = BaseOfficial.nodes.get(sb_id=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
        try:
            experience = Experience(sb_id=exp_id, title=title,
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
        education = Education.nodes.get(sb_id=edu_id)
        return True
    except CypherException as e:
        return e
    except (Education.DoesNotExist, DoesNotExist):
        try:
            rep = BaseOfficial.nodes.get(sb_id=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
        try:
            education = Education(sb_id=edu_id, school_s=school,
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
        rep = BaseOfficial.nodes.get(sb_id=rep_id)
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
        goal = Goal.nodes.get(sb_id=goal_id)
        return goal
    except CypherException as e:
        return e
    except (Goal.DoesNotExist, DoesNotExist):
        try:
            rep = BaseOfficial.nodes.get(sb_id=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
        try:
            goal = Goal(sb_id=goal_id, vote_req=vote_req, money_req=money_req,
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
def save_rep(pleb_username, rep_type, rep_id, recipient_id, customer_id=None):
    try:
        pleb = Pleb.nodes.get(username=pleb_username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    temp_type = dict(settings.BASE_REP_TYPES)[rep_type]
    rep_type = get_rep_type(temp_type)
    try:
        rep = rep_type.nodes.get(sb_id=rep_id)
    except CypherException as e:
        return e
    except (rep_type.DoesNotExist, DoesNotExist):
        rep = rep_type(sb_id=rep_id).save()
    try:
        rep.pleb.connect(pleb)
        pleb.official.connect(rep)
        rep.save()
        pleb.save()
    except CypherException as e:
        return e
    try:
        rep.recipient_id = recipient_id
        if customer_id is not None:
            rep.customer_id = customer_id
        rep.save()
    except CypherException as e:
        return e
    return rep

@apply_defense
def determine_reps(username):
    from sb_docstore.utils import update_base_user_reps
    senators = []
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException):
        return False
    try:
        address = pleb.address.all()[0]
    except (CypherException, IOError, IndexError):
        return False
    pleb_state = address.state
    pleb_district = int(address.congressional_district)
    query = 'match (n:BaseOfficial) where n.state="%s" ' \
            ' return n' % pleb_state
    reps, meta = execute_cypher_query(query)
    if isinstance(reps, Exception):
        return False
    reps = [BaseOfficial.inflate(row[0]) for row in reps]
    for rep in reps:
        if rep.district == pleb_district:
            try:
                pleb.house_rep.connect(rep)
            except (CypherException, IOError):
                return False
            house_rep = rep.sb_id
        elif rep.district is None:
            try:
                pleb.senator.connect(rep)
            except(CypherException, IOError):
                return False
            senators.append(rep.sb_id)
    update_base_user_reps(username, house_rep, senators)
    return {"house_rep": house_rep, "senators": senators}