from django.db import models

class BombermanKeys(models.Model):
    bomberman_id = models.IntegerField(primary_key=True)
    bomberman_key = models.CharField(max_length=36)
    count = models.IntegerField()
    count_limit = models.IntegerField()