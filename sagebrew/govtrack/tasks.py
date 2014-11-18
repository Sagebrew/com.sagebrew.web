from json import dumps
from logging import getLogger
from celery import shared_task
from requests import get
from datetime import datetime

from .utils import create_gt_role
from govtrack.neo_models import (GTPerson, GTCommittee,
                                 GT_RCVotes, GTVoteOption, GTCongressNumbers)
from sb_base.utils import defensive_exception

logger = getLogger('loggly_logs')

@shared_task()
def populate_gt_role(requesturl):
    '''
    This function takes a url which can be converted into a .json file. It
    then converts
    the json into a dict and creates and populates a GTRole object then
    saves it
    to the neo4j server.
    '''
    try:
        role_request = get(requesturl)
        role_data_dict = role_request.json()
        congress_number_object = []
        for rep in role_data_dict['objects']:
            my_role = create_gt_role(rep)
            for number in rep['congress_numbers']:
                try:
                    my_congress_number = GTCongressNumbers.nodes.get(
                        congress_number=number)
                except GTCongressNumbers.DoesNotExist:
                    my_congress_number = GTCongressNumbers()
                    my_congress_number.congress_number = number
                    my_congress_number.save()
                congress_number_object.append(my_congress_number)
            for item in congress_number_object:
                my_role.congress_numbers.connect(item)
            congress_number_object = []
        return True
    except Exception as e:
        raise defensive_exception(populate_gt_role.__name__, e,
                                  populate_gt_role.retry(
                                      exc=e, countdown=3,
                                     max_retries=None))


@shared_task()
def populate_gt_person(requesturl):
    '''
    This function takes a url which can be converted into a .json file. It
    then converts
    the json into a dict and creates and populates a GTPerson object then
    saves it to the
    neo4j server.

    Will eventually create relationships between GTPerson and GTRole.
    '''
    try:
        person_request = get(requesturl)
        person_data_dict = person_request.json()
        for person in person_data_dict['objects']:
            try:
                my_person = GTPerson.nodes.get(gt_id=person["id"])
            except GTPerson.DoesNotExist:
                person["birthday"] = datetime.strptime(person["birthday"],
                                                       '%Y-%m-%d')
                person["gt_id"] = person["id"]
                person.pop("id", None)
                my_person = GTPerson(**person)
                my_person.save()
        return True
    except Exception as e:
        raise defensive_exception(populate_gt_person.__name__,e,
                                  populate_gt_person.retry(
                                      exc=e, countdown=3,
                                     max_retries=None))

@shared_task()
def populate_gt_committee(requesturl):
    '''
    This function takes a url which can be converted into a .json file. It
    then converts
    the json into a dict and creates and populates a GTCommittee object then
    saves
    to the neo4j server.

    Will eventually create relationships between sub committees.
    '''
    try:
        committee_request = get(requesturl)
        committee_data_dict = committee_request.json()
        for committee in committee_data_dict['objects']:
            try:
                my_committee = GTCommittee.nodes.get(committee_id=committee["id"])
            except GTCommittee.DoesNotExist:
                committee["committee_id"] = committee["id"]
                committee.pop("id", None)
                committee.pop("committee", None)
                my_committee = GTCommittee(**committee)
                my_committee.save()
        return True
    except Exception as e:
        raise defensive_exception(populate_gt_committee.__name__, e,
                                  populate_gt_committee.retry(
                                      exc=e, countdown=3,
                                     max_retries=None))


@shared_task()
def populate_gt_votes(requesturl):
    '''
    This function takes a url which can be converted into a .json file. It
    then converts
    the json into a dict and creates and populates a GT_RCVotes object. It
    then also creates
    multiple GTVoteOption objects which are related to the GT_RCVotes object
    that was created.
    It also creates the relationship between the GT_RCVotes and GTVoteOption.
    '''
    try:
        vote_request = get(requesturl)
        vote_data_dict = vote_request.json()
        my_votes = []
        for vote in vote_data_dict['objects']:
            try:
                my_vote = GT_RCVotes.nodes.get(vote_id=vote["id"])
            except GT_RCVotes.DoesNotExist:
                for voteoption in vote['options']:
                    try:
                        my_vote_option = GTVoteOption.nodes.get(
                            option_id=voteoption["id"])
                    except GTVoteOption.DoesNotExist:
                        voteoption["option_id"] = voteoption["id"]
                        voteoption.pop("id", None)
                        my_vote_option = GTVoteOption(**voteoption)
                        my_vote_option.save()
                        my_votes.append(my_vote_option)
                vote.pop("options", None)
                vote["vote_id"] = vote["id"]
                vote.pop("id", None)
                vote["category_one"] = vote["category"]
                vote.pop("category", None)
                my_vote = GT_RCVotes(**vote)
                my_vote.save()
                for item in my_votes:
                    my_vote.option.connect(item)
                my_votes = []
        return True
    except Exception as e:
        raise defensive_exception(populate_gt_votes.__name__, e,
                                  populate_gt_votes.retry(exc=e, countdown=3,
                                     max_retries=None))

