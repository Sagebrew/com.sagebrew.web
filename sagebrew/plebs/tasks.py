from celery import shared_task

from .neo_models import Pleb

@shared_task()
def create_pleb_task(email):
    pass