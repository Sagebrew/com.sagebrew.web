from celery import shared_task
from requests import get
from govtrack.models import Congressman


@shared_task()
def add(x,y):
    return x+y

@shared_task()
def populateCongressman(x):
    congressman_request=get(x)
    congressman_data=congressman_request.json()
    Congressman.objects.create()

