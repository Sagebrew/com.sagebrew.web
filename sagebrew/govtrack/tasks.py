from celery import shared_task
from requests import get
from govtrack.models import Role , Person

@shared_task()
def populaterole(requesturl):
    role_request = get(requesturl)
    role_data_dict = role_request.json()
    for representative in role_data_dict['objects']:
        new_rep = Role.objects.create(**representative)
        new_rep.save()

