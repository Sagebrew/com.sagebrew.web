from datetime import datetime

from govtrack.neo_models import (GTPerson, GTRole)


def create_gt_role(rep):
    try:
        my_role = GTRole.nodes.get(role_id=rep["id"])
    except GTRole.DoesNotExist:
        my_person = create_gt_person(rep['person'])
        rep.pop("person", None)
        rep["role_id"] = rep["id"]
        rep.pop("id", None)
        rep["enddate"] = datetime.strptime(rep["enddate"],
                                           '%Y-%m-%d')
        rep["startdate"] = datetime.strptime(rep["startdate"],
                                             '%Y-%m-%d')
        something = rep.pop("congress_numbers", None)
        my_role = GTRole(**rep)
        my_role.save()
        rep['congress_numbers'] = something
        my_person.role.connect(my_role)
        my_role.person.connect(my_person)
        print "Rep Created"

    return my_role


def create_gt_person(gt_person):
    try:
        my_person = GTPerson.nodes.get(gt_id=gt_person["id"])
    except GTPerson.DoesNotExist:
        gt_person["birthday"] = datetime.strptime(gt_person["birthday"],
                                                  '%Y-%m-%d')
        gt_person["gt_id"] = gt_person["id"]
        gt_person.pop("id", None)
        my_person = GTPerson(**gt_person)
        my_person.save()
        print "Person Created"

    return my_person