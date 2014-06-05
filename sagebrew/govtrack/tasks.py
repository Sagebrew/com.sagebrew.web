from celery import shared_task
from requests import get
from govtrack.models import SRole , Person , GTBill , GTVotes

@shared_task()
def populate_role(requesturl):
    role_request = get(requesturl)
    role_data_dict = role_request.json()
    for representative in role_data_dict['objects']:
        my_person = Person.objects.create(**representative['person'])
        my_person.save()
        representative["person"] = my_person
        new_rep = SRole.objects.create(**representative)
        new_rep.save()

@shared_task()
def populate_gt_bills(requesturl):
    bill_request = get(requesturl)
    bill_data_dict = bill_request.json()
    for bill in bill_data_dict['objects']:
        person_id = bill["sponsor"]["id"]
        role_id = bill["sponsor_role"]["id"]
        bill["sponsor"] = person_id
        bill["sponsor_role"] = role_id
        my_bill = GTBill.objects.create(**bill)
        my_bill.save()

#@shared_task()
#def populate_gt_votes(requesturl):
    #vote_request = get(requesturl)
    #vote_data_dict = vote_request.json()
    #for vote in vote_data_dict['objects']:

