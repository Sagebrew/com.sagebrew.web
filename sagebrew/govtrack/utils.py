from datetime import datetime
from neomodel import DoesNotExist, CypherException
from govtrack.neo_models import (GTPerson, GTRole)


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
