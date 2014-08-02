# Create your models here.
from django.db import models
from model_utils.models import TimeStampedModel

class BombermanKeys(TimeStampedModel):
    bomberman_id = models.IntegerField(primary_key=True)
    bomberman_key = models.CharField(max_length=1000)
    count = models.IntegerField(default=0)
    count_limit = models.IntegerField(default=10)