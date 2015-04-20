import importlib
from django.conf import settings
from django.template.loader import render_to_string

from neomodel import (DoesNotExist, CypherException)

from plebs.neo_models import Pleb
from api.utils import execute_cypher_query
from sb_base.decorators import apply_defense

from .neo_models import (PublicOfficial)


@apply_defense
def save_bio(rep_id, bio):
    try:
        rep = PublicOfficial.nodes.get(object_uuid=rep_id)
    except (CypherException, PublicOfficial.DoesNotExist, DoesNotExist,
            IOError) as e:
        return e
    try:
        rep.bio = bio
        rep.save()
    except (CypherException, IOError) as e:
        return e
    return bio

'''
@apply_defense
def save_goal(rep_id, vote_req, money_req, initial, description, goal_id):
    try:
        goal = Goal.nodes.get(object_uuid=goal_id)
        return goal
    except CypherException as e:
        return e
    except (Goal.DoesNotExist, DoesNotExist):
        try:
            rep = PublicOfficial.nodes.get(object_uuid=rep_id)
        except (PublicOfficial.DoesNotExist, DoesNotExist,
                CypherException) as e:
            return e
        try:
            goal = Goal(object_uuid=goal_id, vote_req=vote_req,
                        money_req=money_req,
                        initial=initial, description=description).save()
        except CypherException as e:
            return e
        try:
            rep.goal.connect(goal)
        except CypherException as e:
            return e
    return goal
'''


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
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        return e
    temp_type = dict(settings.BASE_REP_TYPES)[rep_type]
    rep_type = get_rep_type(temp_type)
    try:
        rep = rep_type.nodes.get(object_uuid=rep_id)
    except (CypherException, IOError) as e:
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
    except (CypherException, IOError) as e:
        return e
    return rep


@apply_defense
def determine_reps(username):
    senators = []
    try:
        pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError):
        return False
    try:
        address = pleb.address.all()[0]
    except (CypherException, IOError, IndexError):
        return False
    pleb_state = address.state
    pleb_district = int(address.congressional_district)
    query = 'match (n:PublicOfficial) where n.state="%s" ' \
            ' return n' % pleb_state
    reps, meta = execute_cypher_query(query)
    if isinstance(reps, Exception):
        return False
    reps = [PublicOfficial.inflate(row[0]) for row in reps]
    for rep in reps:
        if rep.district == pleb_district:
            try:
                pleb.house_rep.connect(rep)
            except (CypherException, IOError):
                return False
        if rep.district == 0:
            try:
                pleb.senators.connect(rep)
            except (CypherException, IOError):
                return False
            senators.append(rep.object_uuid)
    return True


@apply_defense
def prepare_official_search_html(object_uuid):
    try:
        official = PublicOfficial.nodes.get(object_uuid=object_uuid)
    except (PublicOfficial.DoesNotExist, DoesNotExist):
        return False
    except (CypherException, IOError):
        return False
    official_data = official.get_dict()
    return render_to_string("saga_search_block.html", official_data)
