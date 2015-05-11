import yaml
from dateutil import parser
from datetime import datetime
from requests import get

from django.conf import settings

from neomodel import DoesNotExist, CypherException, db
from govtrack.neo_models import (GTPerson, GTRole, GTCongressNumbers,
                                 SenatorTerm, HouseRepTerm)
from sb_public_official.neo_models import PublicOfficial


def create_gt_role(rep):
    try:
        my_role = GTRole.nodes.get(role_id=rep["id"])
    except(GTRole.DoesNotExist, DoesNotExist):
        my_person = create_gt_person(rep['person'])
        rep.pop("person", None)
        rep["role_id"] = rep["id"]
        rep.pop("id", None)
        rep["enddate"] = datetime.strptime(rep["enddate"],
                                           '%Y-%m-%d')
        rep["startdate"] = datetime.strptime(rep["startdate"],
                                             '%Y-%m-%d')
        temp_cong_num = rep.pop("congress_numbers", None)
        my_role = GTRole(**rep)
        try:
            my_role.save()
            rep['congress_numbers'] = temp_cong_num
            my_person.role.connect(my_role)
            my_role.person.connect(my_person)
        except(CypherException, IOError) as e:
            return e
    except(CypherException, IOError) as e:
        return e
    return my_role


def create_gt_person(gt_person):
    try:
        my_person = GTPerson.nodes.get(gt_id=gt_person["id"])
    except(GTPerson.DoesNotExist, DoesNotExist):
        gt_person["birthday"] = datetime.strptime(gt_person["birthday"],
                                                  '%Y-%m-%d')
        gt_person["gt_id"] = gt_person["id"]
        gt_person.pop("id", None)
        my_person = GTPerson(**gt_person)
        try:
            my_person.save()
        except(CypherException, IOError) as e:
            return e
    except(CypherException, IOError) as e:
        return e

    return my_person


def populate_gt_roles_util(requesturl):
    role_request = get(requesturl)

    role_data_dict = role_request.json()
    congress_number_object = []
    for rep in role_data_dict['objects']:
        my_role = create_gt_role(rep)
        for number in rep['congress_numbers']:
            try:
                my_congress_number = GTCongressNumbers.nodes.get(
                    congress_number=number)
            except(GTCongressNumbers.DoesNotExist, DoesNotExist):
                my_congress_number = GTCongressNumbers()
                my_congress_number.congress_number = number
                try:
                    my_congress_number.save()
                except (CypherException, IOError) as e:
                    return e
            except (CypherException, IOError) as e:
                return e
            congress_number_object.append(my_congress_number)
        for item in congress_number_object:
            my_role.congress_numbers.connect(item)
        congress_number_object = []
    return True


def populate_term_data():
    yaml_data = yaml.load(
        open(settings.YAML_FILES + "legislators-current.yaml"))
    now = datetime.now()
    for person in yaml_data:
        sb_person = PublicOfficial.nodes.get(gt_id=person['id']['govtrack'])
        for term in person['terms']:
            term['start'] = parser.parse(term['start'])
            term['end'] = parser.parse(term['end'])
            term['current'] = False
            if now < term['end']:
                term['current'] = True
            if term['type'] == 'sen':
                term['sen_class'] = term.pop('class', None)
                sen_term = SenatorTerm(**term).save()
                if term['current']:
                    current_type = sen_term
                sb_person.sen_terms.connect(sen_term)
            if term['type'] == 'rep':
                rep_term = HouseRepTerm(**term).save()
                if term['current']:
                    current_type = rep_term
                sb_person.house_terms.connect(rep_term)
        print current_type.state, current_type.district
        query = 'MATCH (p:PublicOfficial {gt_id: %s})--(t:%s) WHERE ' \
                't.state="%s" RETURN t' % (sb_person.gt_id,
                                                           current_type.
                                                           labels()[-1],
                                                           current_type.state)
        print query
        res, col = db.cypher_query(query)
        print res, col
        print len(res), len(col)
        print

    return True
