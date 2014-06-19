from celery import shared_task
from requests import get
from datetime import datetime
from govtrack.neo_models import GTPerson, GTRole, GTCommittee, GT_RCVotes, GTVoteOption


'''
This function takes a url which can be converted into a .json file. It then converts
the json into a dict and creates and populates a GTRole object then saves it
to the neo4j server.

This function needs to be updated because populating the person object is no longer
necissary because we have another function for that, but we still need to populate the
GTRole objects and create the relationship.

@shared_task()
def populate_gt_role(requesturl):
    role_request = get(requesturl)
    role_data_dict = role_request.json()
    for rep in role_data_dict['objects']:
        try:
            my_role = GTRole.index.get(id=rep["id"])
        except GTRole.DoesNotExist:
            my_person = GTPerson(**rep['person'])
            my_person.save()
            rep["person"] = my_person
            my_role = GTRole(**rep)
            my_role.save()
'''

'''
This function takes a url which can be converted into a .json file. It then converts
the json into a dict and creates and populates a GTPerson object then saves it to the
neo4j server.

Will eventually create relationships between GTPerson and GTRole.
'''
@shared_task()
def populate_gt_person(requesturl):
    person_request = get(requesturl)
    person_data_dict = person_request.json()
    for person in person_data_dict['objects']:
        try:
            my_person = GTPerson.index.get(gt_id=person["id"])
        except GTPerson.DoesNotExist:
            person["birthday"] = datetime.strptime(person["birthday"],
                                                   '%Y-%m-%d')
            person["gt_id"] = person["id"]
            person.pop("id", None)
            my_person = GTPerson(**person)
            my_person.save()

'''
This function takes a url which can be converted into a .json file. It then converts
the json into a dict and creates and populates a GTCommittee object then saves
to the neo4j server.

Will eventually create relationships between sub committees.
'''
@shared_task()
def populate_gt_committee(requesturl):
    committee_request = get(requesturl)
    committee_data_dict = committee_request.json()
    for committee in committee_data_dict['objects']:
        try:
            my_committee = GTCommittee.index.get(committee_id = committee["id"])
        except GTCommittee.DoesNotExist:
            committee["committee_id"] = committee["id"]
            committee.pop("id", None)
            committee.pop("committee", None)
            my_committee = GTCommittee(**committee)
            my_committee.save()

'''
his function takes a url which can be converted into a .json file. It then converts
the json into a dict and creates and populates a GT_RCVotes object. It then also creates
multiple GTVoteOption objects which are related to the GT_RCVotes object that was created.
It also creates the relationship between the GT_RCVotes and GTVoteOption.
'''
@shared_task()
def populate_gt_votes(requesturl):
    vote_request = get(requesturl)
    vote_data_dict = vote_request.json()
    my_votes = []
    for vote in vote_data_dict['objects']:
        try:
            my_vote = GT_RCVotes.index.get(vote_id = vote["id"])
        except GT_RCVotes.DoesNotExist:
            for voteoption in vote['options']:
                try:
                    my_vote_option = GTVoteOption.index.get(option_id = voteoption["id"])
                except GTVoteOption.DoesNotExist:
                    vote["option_id"] = vote["id"]
                    vote.pop("id", None)
                    my_vote_option = GTVoteOption(**voteoption)
                    my_vote_option.save()
                    my_votes.append(my_vote_option)
            vote.pop("options", None)
            vote["vote_id"] =vote["id"]
            vote.pop("id", None)
            vote["category_one"] = vote["category"]
            vote.pop("category", None)
            my_vote = GT_RCVotes(**vote)
            my_vote.save()
            for item in my_votes:
                my_vote.option.connect(item)
            my_votes = []


