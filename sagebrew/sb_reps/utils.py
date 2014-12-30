from dateutil import parser
from neomodel import (DoesNotExist, CypherException)

from .neo_models import Policy, BaseOfficial, Experience, Education
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