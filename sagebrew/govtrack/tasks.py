from celery import Celery
from celery import shared_task
app = Celery('tasks', broker='amqp://guest@localhost//')

@shared_task()
def add(x,y):
    return x+y
